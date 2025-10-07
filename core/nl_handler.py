import logging
from typing import Any, Dict, List

from core.llm_caller import LLMCaller

logger = logging.getLogger(__name__)


class NLHandler:
    """
    Handler mínimo para conversação em linguagem natural.
    Encapsula chamadas a LLM e integra com memória vetorial (placeholder).
    """

    def __init__(self, llm_config: Dict[str, Any] | None = None):
        self.llm = LLMCaller(llm_config)

    def chat(self, user_message: str, context: List[str] | None = None) -> str:
        prompt = self._build_prompt(user_message, context or [])
        logger.info("Chamando LLM para responder ao usuário")
        return self.llm.call(prompt)

    def _build_prompt(self, message: str, context: List[str]) -> str:
        ctx = "\n".join(context[-6:]) if context else ""
        return f"Context:\n{ctx}\n\nUser: {message}\nAssistant:"
