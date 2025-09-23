"""LLM adapters: provide a single interface for generation and embeddings.
Falls back to deterministic/local responses if no external API keys.
"""
import os
import logging
from typing import Dict, List

log = logging.getLogger('llm_adapters')

class LLMAdapter:
    def __init__(self):
        self.provider = None
        if os.environ.get('OPENAI_API_KEY'):
            try:
                import openai
                self.provider = 'openai'
                self.openai = openai
            except Exception:
                log.warning('openai library not available')
        elif os.environ.get('GEMINI_API_KEY'):
            self.provider = 'gemini'
        else:
            self.provider = 'local'

    def generate(self, prompt: str, **kwargs) -> str:
        if self.provider == 'openai':
            try:
                resp = self.openai.ChatCompletion.create(model='gpt-4o', messages=[{'role':'user','content':prompt}])
                return resp.choices[0].message.content
            except Exception as e:
                log.exception('OpenAI request failed, falling back to local: %s', e)
        # local fallback deterministic: echo with small transform
        return f"[local-fallback] {prompt[:800]}"

    def embed(self, text: str) -> List[float]:
        # If embeddings available via provider implement; otherwise simple hash vector
        if self.provider == 'openai':
            try:
                resp = self.openai.Embedding.create(input=text, model='text-embedding-3-small')
                return resp.data[0].embedding
            except Exception:
                log.exception('OpenAI embedding failed; using fallback')
        # fallback: simple deterministic vector from hash
        h = abs(hash(text))
        vec = [(h >> (i*8)) % 256 / 255.0 for i in range(128)]
        return vec
