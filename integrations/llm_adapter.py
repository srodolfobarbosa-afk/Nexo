import logging
import os
from typing import Any, Dict, Optional

logger = logging.getLogger("llm_adapter")


def get_llm_provider() -> str:
    return os.environ.get("NEXO_LLM_PROVIDER", "openai")


def call_llm(prompt: str, **kwargs) -> Dict[str, Any]:
    provider = get_llm_provider().lower()
    if provider == "openai":
        return _call_openai(prompt, **kwargs)
    elif provider in ("google", "gemini"):
        return _call_gemini(prompt, **kwargs)
    elif provider == "local":
        return _call_local(prompt, **kwargs)
    else:
        raise RuntimeError(f"Unknown LLM provider: {provider}")


def _call_openai(prompt: str, **kwargs) -> Dict[str, Any]:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        logger.warning("OPENAI_API_KEY not set; returning stub response")
        return {"text": "[stub] openai unavailable"}
    # Lazy import to avoid mandating openai in all environments
    try:
        import openai

        openai.api_key = api_key
        resp = openai.ChatCompletion.create(
            model=kwargs.get("model", "gpt-4o"),
            messages=[{"role": "user", "content": prompt}],
            max_tokens=kwargs.get("max_tokens", 512),
        )
        return {"text": resp.choices[0].message.content}
    except Exception as e:
        logger.exception("OpenAI call failed")
        return {"error": str(e)}


def _call_gemini(prompt: str, **kwargs) -> Dict[str, Any]:
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        logger.warning("GEMINI_API_KEY not set; returning stub response")
        return {"text": "[stub] gemini unavailable"}
    # Placeholder: implement gemini/api as needed
    return {"text": "[stub] gemini call (not implemented)"}


def _call_local(prompt: str, **kwargs) -> Dict[str, Any]:
    # simple local fallback for testing
    return {"text": f"[local echo] {prompt[:200]}"}
