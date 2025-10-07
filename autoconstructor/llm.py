import os
from typing import Optional

try:
    from transformers import pipeline
except Exception:
    pipeline = None


def get_openai_key():
    return os.environ.get("OPENAI_API_KEY")


def generate_text(prompt: str, model: Optional[str] = None) -> str:
    """Try OpenAI first, fallback to local transformers pipeline if available."""
    openai_key = get_openai_key()
    if openai_key:
        # use openai package if available
        try:
            import openai

            openai.api_key = openai_key
            resp = openai.Completion.create(
                model=model or "text-davinci-003", prompt=prompt, max_tokens=512
            )
            return resp.choices[0].text.strip()
        except Exception:
            pass

    if pipeline is not None:
        try:
            gen = pipeline("text-generation", model=model or "gpt2")
            out = gen(prompt, max_length=512, do_sample=False)
            return out[0]["generated_text"]
        except Exception:
            pass

    # fallback message
    return """[LLM Unavailable] No OPENAI_API_KEY and no local transformers pipeline available. Please configure one to use LLM features."""
