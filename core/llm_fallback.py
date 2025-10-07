"""Módulo de fallback para provedores LLM.

Fornece uma API simples: select_provider() retorna um dict com nome e função de chamada.
Também expõe call_with_fallback(prompt, **kwargs) que tenta provedores na ordem configurada.
"""

import logging
import os
from typing import Any, Callable, Dict, List, Optional

from .supabase_client import save_log

logger = logging.getLogger("llm_fallback")


def _has_key(name: str) -> bool:
    return bool(os.environ.get(name))


def available_providers() -> List[str]:
    # Ordem de preferência
    providers = []
    if _has_key("GEMINI_API_KEY"):
        providers.append("gemini")
    if _has_key("OPENAI_API_KEY"):
        providers.append("openai")
    if _has_key("GROQ_API_KEY"):
        providers.append("groq")
    if _has_key("OLLAMA_HOST") or _has_key("OLLAMA_API_KEY"):
        providers.append("ollama")
    return providers


def select_provider(preferred: Optional[str] = None) -> Optional[str]:
    providers = available_providers()
    if preferred and preferred in providers:
        return preferred
    return providers[0] if providers else None


def _record_fallback_event(
    prev_provider: Optional[str], tried_provider: str, reason: str
):
    try:
        save_log(
            "warning",
            f"LLM fallback: {prev_provider} -> {tried_provider}",
            {"reason": reason},
        )
    except Exception:
        logger.debug("Não foi possível salvar fallback no Supabase.")


def call_with_fallback(
    prompt: str,
    model: Optional[str] = None,
    timeout: int = 20,
    preferred: Optional[str] = None,
    **kwargs,
) -> Dict[str, Any]:
    """Tenta chamar provedores em ordem, retornando o primeiro sucesso. Registra eventos de fallback no Supabase quando possível."""
    import time

    providers = available_providers()
    if preferred and preferred in providers:
        providers.remove(preferred)
        providers.insert(0, preferred)

    if not providers:
        logger.error("Nenhum provedor LLM configurado.")
        return {"provider": None, "response": "Erro: nenhum provedor LLM configurado."}

    last_exc = None
    prev = None
    for p in providers:
        try:
            logger.info(f"Tentando LLM provider: {p}")
            if p == "gemini":
                try:
                    import google.generativeai as genai

                    key = os.environ.get("GEMINI_API_KEY")
                    if key:
                        genai.configure(api_key=key)
                    model_name = model or os.environ.get(
                        "GEMINI_MODEL", "gemini-1.5-flash"
                    )
                    resp = genai.generate_text(model=model_name, prompt=prompt)
                    text = str(resp)
                    return {"provider": "gemini", "response": text}
                except Exception as e:
                    last_exc = e
                    _record_fallback_event(prev, "gemini", str(e))
                    logger.warning(f"Gemini falhou: {e}")
            elif p == "openai":
                try:
                    import openai

                    openai.api_key = os.environ.get("OPENAI_API_KEY")
                    model_name = model or os.environ.get("OPENAI_MODEL", "gpt-4o")
                    resp = openai.ChatCompletion.create(
                        model=model_name,
                        messages=[{"role": "user", "content": prompt}],
                        timeout=timeout,
                    )
                    text = (
                        resp.choices[0].message.content
                        if hasattr(resp, "choices")
                        else str(resp)
                    )
                    return {"provider": "openai", "response": text}
                except Exception as e:
                    last_exc = e
                    _record_fallback_event(prev, "openai", str(e))
                    logger.warning(f"OpenAI falhou: {e}")
            elif p == "groq":
                try:
                    import groq

                    model_name = model or os.environ.get("GROQ_MODEL", "gpt-j")
                    text = groq.generate(prompt)
                    return {"provider": "groq", "response": text}
                except Exception as e:
                    last_exc = e
                    _record_fallback_event(prev, "groq", str(e))
                    logger.warning(f"GROQ falhou: {e}")
            elif p == "ollama":
                try:
                    import ollama

                    model_name = model or os.environ.get("OLLAMA_MODEL", "ollama")
                    resp = ollama.generate(model=model_name, prompt=prompt)
                    text = resp.get("text") if isinstance(resp, dict) else str(resp)
                    return {"provider": "ollama", "response": text}
                except Exception as e:
                    last_exc = e
                    _record_fallback_event(prev, "ollama", str(e))
                    logger.warning(f"Ollama falhou: {e}")
        except Exception as e:
            last_exc = e
            _record_fallback_event(prev, p, str(e))
            logger.warning(f"Provider {p} erro inesperado: {e}")
        prev = p

    logger.error(f"Todos provedores falharam. Último erro: {last_exc}")
    return {
        "provider": None,
        "response": f"Erro: todos provedores falharam. Último: {last_exc}",
    }
