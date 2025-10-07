import logging
import os
from typing import Any, Dict, Optional

# Importar clientes das LLMs
try:
    import google.generativeai as genai
except ImportError:
    genai = None
try:
    import openai
except ImportError:
    openai = None
try:
    import groq
except ImportError:
    groq = None

logger = logging.getLogger(__name__)


class LLMCaller:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}

    def call(self, prompt: str, model: str = "auto", **kwargs) -> str:
        # Support a fake LLM mode for CI/dev to avoid external network calls
        if os.environ.get("FAKE_LLM", "false").lower() in ("1", "true", "yes"):
            logging.info("LLMCaller: FAKE_LLM enabled — returning canned response")
            return '{"action": "clarify", "use_auto_construction": false, "response": "fake response from FAKE_LLM mode"}'
        """
        Chama a LLM disponível seguindo ordem de prioridade/fallback.
        model: "gemini", "openai", "groq" ou "auto" (tenta todas)
        """
        errors = []
        if model in ("gemini", "auto") and genai:
            try:
                return self._call_gemini(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Erro Gemini: {e}")
                errors.append(str(e))
        if model in ("openai", "auto") and openai:
            try:
                return self._call_openai(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Erro OpenAI: {e}")
                errors.append(str(e))
        if model in ("groq", "auto") and groq:
            try:
                return self._call_groq(prompt, **kwargs)
            except Exception as e:
                logger.warning(f"Erro Groq: {e}")
                errors.append(str(e))
        raise RuntimeError(f"Nenhuma LLM disponível ou todas falharam: {errors}")

    def _call_gemini(self, prompt: str, **kwargs) -> str:
        # Exemplo: ajuste conforme sua API
        model = self.config.get("gemini_model", "gemini-pro")
        api_key = self.config.get("gemini_api_key")
        if not api_key:
            raise ValueError("API key Gemini não configurada")
        genai.configure(api_key=api_key)
        response = genai.generate_content(model=model, prompt=prompt, **kwargs)
        return response.text if hasattr(response, "text") else str(response)

    def _call_openai(self, prompt: str, **kwargs) -> str:
        model = self.config.get("openai_model", "gpt-3.5-turbo")
        api_key = self.config.get("openai_api_key")
        if not api_key:
            raise ValueError("API key OpenAI não configurada")
        openai.api_key = api_key
        response = openai.ChatCompletion.create(
            model=model, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        return response["choices"][0]["message"]["content"]

    def _call_groq(self, prompt: str, **kwargs) -> str:
        model = self.config.get("groq_model", "llama2-70b-4096")
        api_key = self.config.get("groq_api_key")
        if not api_key:
            raise ValueError("API key Groq não configurada")
        groq.api_key = api_key
        response = groq.ChatCompletion.create(
            model=model, messages=[{"role": "user", "content": prompt}], **kwargs
        )
        return response["choices"][0]["message"]["content"]
