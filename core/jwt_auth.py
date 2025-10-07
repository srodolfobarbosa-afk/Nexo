import base64
import hashlib
import hmac
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Optional

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

logger = logging.getLogger("jwt_auth")

# Secret para assinatura — em produção usar variável de ambiente segura
JWT_SECRET = os.environ.get("JWT_SECRET", "dev-secret-change-me").encode("utf-8")
JWT_EXP_MINUTES = int(os.environ.get("JWT_EXP_MINUTES", "60"))
USE_SUPABASE_AUTH = os.environ.get("USE_SUPABASE_AUTH", "0") in ("1", "true", "True")
SUPABASE_URL = os.environ.get("SUPABASE_URL")

# JWKS cache: {kid -> pem_public_key}
_JWKS_CACHE: Dict[str, str] = {}
_JWKS_LAST_FETCH = 0
_JWKS_TTL = 300


# Tentar importar python-jose; se não estiver disponível, fornecer fallback simples
try:
    from jose import JWTError, jwt  # type: ignore

    _HAVE_JOSE = True
except Exception:
    _HAVE_JOSE = False


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(subject: str, scopes: Optional[list] = None) -> str:
    now = datetime.utcnow()
    exp = now + timedelta(minutes=JWT_EXP_MINUTES)
    payload = {
        "sub": subject,
        "scopes": scopes or [],
        "iat": int(now.timestamp()),
        "exp": int(exp.timestamp()),
    }
    if _HAVE_JOSE:
        return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

    # Fallback: compact token with header.payload.signature where signature is HMAC-SHA256
    header = {"alg": "HS256", "typ": "JWT"}
    header_b = _b64encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b = _b64encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b}.{payload_b}".encode("utf-8")
    sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
    sig_b = _b64encode(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def verify_token(token: str) -> dict:
    # If SUPABASE OIDC flow enabled, try RS256 verification via JWKS first
    if USE_SUPABASE_AUTH and SUPABASE_URL:
        try:
            payload = _verify_jwt_via_jwks(token)
            return payload
        except Exception as e:
            logger.warning(f"JWKS verification failed: {e}")

    if _HAVE_JOSE:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
            return payload
        except JWTError as e:
            logger.warning(f"JWT verification failed: {e}")
            raise

    try:
        header_b, payload_b, sig_b = token.split(".")
        signing_input = f"{header_b}.{payload_b}".encode("utf-8")
        expected_sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64decode(sig_b), expected_sig):
            raise ValueError("invalid signature")
        payload_json = _b64decode(payload_b)
        payload = json.loads(payload_json)
        # checar exp
        if "exp" in payload:
            if int(datetime.utcnow().timestamp()) > int(payload["exp"]):
                raise ValueError("token expired")
        return payload
    except Exception as e:
        logger.warning(f"JWT verification failed (fallback): {e}")
        raise


def _fetch_jwks() -> Dict[str, str]:
    """Fetch JWKS from Supabase URL and cache PEM keys by kid."""
    global _JWKS_LAST_FETCH, _JWKS_CACHE
    now = time.time()
    if _JWKS_CACHE and now - _JWKS_LAST_FETCH < _JWKS_TTL:
        return _JWKS_CACHE
    if not SUPABASE_URL:
        raise RuntimeError("SUPABASE_URL not configured")
    jwks_url = SUPABASE_URL.rstrip("/") + "/.well-known/jwks.json"
    r = requests.get(jwks_url, timeout=5)
    r.raise_for_status()
    jwks = r.json()
    keys = {}
    for key in jwks.get("keys", []):
        kid = key.get("kid")
        kty = key.get("kty")
        if kty != "RSA":
            continue
        n_b = int.from_bytes(_b64decode(key["n"]), "big")
        e_b = int.from_bytes(_b64decode(key["e"]), "big")
        pub = rsa.RSAPublicNumbers(e_b, n_b).public_key()
        pem = pub.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        keys[kid] = pem.decode("utf-8")
    _JWKS_CACHE = keys
    _JWKS_LAST_FETCH = now
    return keys


def _verify_jwt_via_jwks(token: str) -> dict:
    # header to find kid
    header_b64 = token.split(".", 1)[0]
    header = json.loads(_b64decode(header_b64))
    kid = header.get("kid")
    keys = _fetch_jwks()
    if kid not in keys:
        raise ValueError("kid not found in JWKS")
    pem = keys[kid].encode("utf-8")
    # verify signature using cryptography (RS256)
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("invalid token format")
    signing_input = (parts[0] + "." + parts[1]).encode("utf-8")
    sig = _b64decode(parts[2])
    pub = serialization.load_pem_public_key(pem)
    try:
        pub.verify(sig, signing_input, padding.PKCS1v15(), hashes.SHA256())
    except Exception as e:
        raise ValueError(f"RS256 verification failed: {e}")
    payload = json.loads(_b64decode(parts[1]))
    if "exp" in payload and int(datetime.utcnow().timestamp()) > int(payload["exp"]):
        raise ValueError("token expired")
    return payload


def require_jwt(fn):
    """Decorator Flask-friendly to exigir Authorization: Bearer <token> e injetar payload como `g.jwt_payload`.

    Uso:
        @app.route('/api/foo')
        @require_jwt
        def foo():
            payload = g.jwt_payload
            ...
    """
    from functools import wraps

    from flask import g, jsonify, make_response, request

    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth = request.headers.get("Authorization", "")
        if not auth.startswith("Bearer "):
            return make_response(jsonify({"error": "missing_token"}), 401)
        token = auth.split(" ", 1)[1]
        try:
            payload = verify_token(token)
        except Exception:
            return make_response(jsonify({"error": "invalid_token"}), 401)
        g.jwt_payload = payload
        return fn(*args, **kwargs)

    return wrapper


def _warn_if_dev_secret():
    if JWT_SECRET == b"dev-secret-change-me":
        logger.warning(
            "Using default dev JWT_SECRET — replace with a strong secret in production!"
        )


_warn_if_dev_secret()
