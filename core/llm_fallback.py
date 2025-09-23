"""Módulo de fallback para provedores LLM.

Fornece uma API simples: select_provider() retorna um dict com nome e função de chamada.
Também expõe call_with_fallback(prompt, **kwargs) que tenta provedores na ordem configurada.
"""
import os
import logging
from typing import Optional, Callable, List, Dict, Any

logger = logging.getLogger("llm_fallback")


def _has_key(name: str) -> bool:
    return bool(os.environ.get(name))


def available_providers() -> List[str]:
    # Ordem de preferência
    providers = []
    if _has_key('GEMINI_API_KEY'):
        providers.append('gemini')
    if _has_key('OPENAI_API_KEY'):
        providers.append('openai')
    if _has_key('GROQ_API_KEY'):
        providers.append('groq')
    if _has_key('OLLAMA_HOST') or _has_key('OLLAMA_API_KEY'):
        providers.append('ollama')
    return providers


def select_provider(preferred: Optional[str] = None) -> Optional[str]:
    """Retorna o nome de um provedor disponível, respeitando preferência se possível."""
    providers = available_providers()
    if preferred and preferred in providers:
        return preferred
    return providers[0] if providers else None


def call_with_fallback(prompt: str, model: Optional[str] = None, timeout: int = 20, preferred: Optional[str] = None, **kwargs) -> Dict[str, Any]:
    """Tenta chamar provedores em ordem, retornando o primeiro sucesso.

    Retorna dict: { 'provider': name, 'response': text }
    Em falha, retorna {'provider': None, 'response': 'error: ...'}
    """
    import time

    providers = available_providers()
    if preferred and preferred in providers:
        providers.remove(preferred)
        providers.insert(0, preferred)

    if not providers:
        logger.error("Nenhum provedor LLM configurado.")
        return {"provider": None, "response": "Erro: nenhum provedor LLM configurado."}

    last_exc = None
    for p in providers:
        try:
            logger.info(f"Tentando LLM provider: {p}")
            if p == 'gemini':
                try:
                    import google.generativeai as genai
                    key = os.environ.get('GEMINI_API_KEY')
                    if key:
                        genai.configure(api_key=key)
                    model_name = model or os.environ.get('GEMINI_MODEL', 'gemini-1.5-flash')
                    resp = genai.generate_text(model=model_name, prompt=prompt)
                    text = str(resp)
                    return {"provider": 'gemini', "response": text}
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Gemini falhou: {e}")
            elif p == 'openai':
                try:
                    import openai
                    openai.api_key = os.environ.get('OPENAI_API_KEY')
                    model_name = model or os.environ.get('OPENAI_MODEL', 'gpt-4o')
                    resp = openai.ChatCompletion.create(model=model_name, messages=[{"role": "user", "content": prompt}], timeout=timeout)
                    text = resp.choices[0].message.content if hasattr(resp, 'choices') else str(resp)
                    return {"provider": 'openai', "response": text}
                except Exception as e:
                    last_exc = e
                    logger.warning(f"OpenAI falhou: {e}")
            elif p == 'groq':
                try:
                    # groq client import if available
                    import groq
                    key = os.environ.get('GROQ_API_KEY')
                    # Exemplo simplificado — adapte conforme lib real
                    model_name = model or os.environ.get('GROQ_MODEL', 'gpt-j')
                    text = groq.generate(prompt)
                    return {"provider": 'groq', "response": text}
                except Exception as e:
                    last_exc = e
                    logger.warning(f"GROQ falhou: {e}")
            elif p == 'ollama':
                try:
                    import ollama
                    model_name = model or os.environ.get('OLLAMA_MODEL', 'ollama')
                    resp = ollama.generate(model=model_name, prompt=prompt)
                    text = resp.get('text') if isinstance(resp, dict) else str(resp)
                    return {"provider": 'ollama', "response": text}
                except Exception as e:
                    last_exc = e
                    logger.warning(f"Ollama falhou: {e}")
        except Exception as e:
            last_exc = e
            logger.warning(f"Provider {p} erro inesperado: {e}")

    logger.error(f"Todos provedores falharam. Último erro: {last_exc}")
    return {"provider": None, "response": f"Erro: todos provedores falharam. Último: {last_exc}"}
