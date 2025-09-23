import os
import logging
from datetime import datetime, timedelta
from typing import Optional
import json
import base64
import hmac
import hashlib

logger = logging.getLogger('jwt_auth')

# Secret para assinatura — em produção usar variável de ambiente segura
JWT_SECRET = os.environ.get('JWT_SECRET', 'dev-secret-change-me').encode('utf-8')
JWT_EXP_MINUTES = int(os.environ.get('JWT_EXP_MINUTES', '60'))


# Tentar importar python-jose; se não estiver disponível, fornecer fallback simples
try:
    from jose import JWTError, jwt  # type: ignore
    _HAVE_JOSE = True
except Exception:
    _HAVE_JOSE = False


def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode('ascii')


def _b64decode(data: str) -> bytes:
    padding = '=' * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def create_token(subject: str, scopes: Optional[list] = None) -> str:
    now = datetime.utcnow()
    exp = now + timedelta(minutes=JWT_EXP_MINUTES)
    payload = {
        'sub': subject,
        'scopes': scopes or [],
        'iat': int(now.timestamp()),
        'exp': int(exp.timestamp())
    }
    if _HAVE_JOSE:
        return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

    # Fallback: compact token with header.payload.signature where signature is HMAC-SHA256
    header = {'alg': 'HS256', 'typ': 'JWT'}
    header_b = _b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
    payload_b = _b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
    signing_input = f"{header_b}.{payload_b}".encode('utf-8')
    sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
    sig_b = _b64encode(sig)
    return f"{header_b}.{payload_b}.{sig_b}"


def verify_token(token: str) -> dict:
    if _HAVE_JOSE:
        try:
            payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            return payload
        except JWTError as e:
            logger.warning(f'JWT verification failed: {e}')
            raise

    try:
        header_b, payload_b, sig_b = token.split('.')
        signing_input = f"{header_b}.{payload_b}".encode('utf-8')
        expected_sig = hmac.new(JWT_SECRET, signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(_b64decode(sig_b), expected_sig):
            raise ValueError('invalid signature')
        payload_json = _b64decode(payload_b)
        payload = json.loads(payload_json)
        # checar exp
        if 'exp' in payload:
            if int(datetime.utcnow().timestamp()) > int(payload['exp']):
                raise ValueError('token expired')
        return payload
    except Exception as e:
        logger.warning(f'JWT verification failed (fallback): {e}')
        raise
