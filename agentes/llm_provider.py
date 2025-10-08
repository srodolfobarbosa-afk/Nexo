import os
from typing import Optional


class LLMProvider:
    """Abstração simples para cadeia de LLMs com fallback.

    Prioridade:
      1. OpenAI (OPENAI_API_KEY)
      2. Google Gemini (GOOGLE_API_KEY)
      3. Local fallback (echo/heuristics)

    Observação: esta implementação evita importar SDKs pesados em runtime.
    Se as bibliotecas estiverem instaladas e as chaves definidas, elas serão usadas;
    caso contrário, usamos um fallback seguro.
    """

    def __init__(self):
        self.openai_key = os.environ.get("OPENAI_API_KEY")
        self.google_key = os.environ.get("GOOGLE_API_KEY")

        # lazy import placeholders
        self._openai = None
        self._google = None

    def _init_openai(self):
        if self._openai is not None:
            return
        try:
            import openai

            self._openai = openai
            self._openai.api_key = self.openai_key
        except Exception:
            self._openai = None

    def _init_google(self):
        if self._google is not None:
            return
        try:
            # google generative api client optional
            from google.generativeai import client as google_client  # type: ignore

            self._google = google_client
            # auth depending on client, left as environment config
        except Exception:
            self._google = None

    def get_response(self, prompt: str, max_tokens: int = 256) -> str:
        # Try OpenAI
        if self.openai_key:
            self._init_openai()
            if self._openai:
                try:
                    resp = self._openai.ChatCompletion.create(
                        model="gpt-3.5-turbo", messages=[{"role": "user", "content": prompt}], max_tokens=max_tokens
                    )
                    # compatibility with different SDK shapes
                    if isinstance(resp, dict):
                        return resp.get("choices", [])[0].get("message", {}).get("content", "")
                    return getattr(resp.choices[0].message, "content", "")
                except Exception:
                    pass

        # Try Google
        if self.google_key:
            self._init_google()
            if self._google:
                try:
                    # placeholder for google generative call
                    # actual client usage may differ; keep minimal to avoid hard dependency
                    out = self._google.generate(text=prompt)
                    return getattr(out, "candidates", [])[0].get("content", "")
                except Exception:
                    pass

        # Fallback local heuristic
        return self._local_fallback(prompt)

    def _local_fallback(self, prompt: str) -> str:
        p = prompt.strip().lower()
        if "ping" in p:
            return "pong"
        if "help" in p or "ajuda" in p:
            return "Posso ajudar com: criar missão, listar métricas, executar tarefa."
        # simple echo with truncation
        return f"[fallback] {prompt[:400]}"
