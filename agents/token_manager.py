import os
from typing import Optional
try:
    # Prefer absolute import so tests and CI can import packages from repo root
    from autoconstructor.secrets_provider import get_secret
except Exception:  # pragma: no cover - fallback for different import contexts
    # Fallback to relative import if running as a package
    from ..autoconstructor.secrets_provider import get_secret


class TokenManager:
    """Simple token manager that retrieves tokens from environment or secrets provider.

    Tokens supported:
    - GITHUB_TOKEN
    - KEL_TOKEN (example of API Kel)
    - OPENAI_API_KEY
    """

    @staticmethod
    def get_token(name: str) -> Optional[str]:
        # Try explicit env var first
        env_name = name.upper()
        v = os.environ.get(env_name)
        if v:
            return v
        # fallback to centralized secrets provider
        return get_secret(env_name)
