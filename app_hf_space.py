import gradio as gr
import os
import requests
from transformers import pipeline
from pathlib import Path


def load_summarizer():
    # Modelo leve para summarization. Em Spaces você pode trocar para um melhor se tiver GPU.
    model_name = "google/flan-t5-small"
    summarizer = pipeline("summarization", model=model_name, tokenizer=model_name)
    return summarizer


SUMMARIZER = None


def summarize_text(text: str, max_length: int = 150):
    global SUMMARIZER
    if not text or not text.strip():
        return "Por favor, insira um texto ou carregue um arquivo .txt"

    # Se existir chave HUGGINGFACE_API_KEY, usar a Inference API em vez do pipeline local
    hf_key = os.environ.get("HUGGINGFACE_API_KEY")
    if hf_key:
        try:
            api_url = "https://api-inference.huggingface.co/models/google/flan-t5-small"
            headers = {"Authorization": f"Bearer {hf_key}", "Accept": "application/json"}
            payload = {"inputs": text, "parameters": {"max_new_tokens": int(max_length)}}
            resp = requests.post(api_url, headers=headers, json=payload, timeout=60)
            resp.raise_for_status()
            data = resp.json()
            # A API pode retornar string direto ou um objeto; tentamos extrair
            if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
                return data[0].get("generated_text", str(data[0]))
            if isinstance(data, dict) and "generated_text" in data:
                return data["generated_text"]
            return str(data)
        except Exception as e:
            # Se falhar, cair para o pipeline local
            print(f"⚠️ Erro na Inference API, fallback para pipeline local: {e}")

    if SUMMARIZER is None:
        SUMMARIZER = load_summarizer()

    # Não enviar textos muito longos em uma única chamada para modelos pequenos
    # Aqui fazemos uma chamada direta; para produção é melhor chunking + sumarização incremental
    try:
        summary = SUMMARIZER(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]["summary_text"]
    except Exception as e:
        return f"Erro durante a sumarização: {e}"


def file_to_text(file_obj):
    if file_obj is None:
        return ""
    p = Path(file_obj.name)
    try:
        data = p.read_text(encoding="utf-8")
        return data
    except Exception:
        # Fallback: use file-like read
        try:
            file_obj.seek(0)
            return file_obj.read().decode("utf-8", errors="ignore")
        except Exception as e:
            return f"Erro ao ler arquivo: {e}"


with gr.Blocks(title="Nexo — Summarization (Gradio)") as demo:
    gr.Markdown("# Nexo Summarization Demo\n\nCarregue um arquivo .txt ou cole o texto e clique em 'Summarize'.")

    with gr.Row():
        with gr.Column(scale=3):
            input_text = gr.Textbox(lines=12, label="Texto de entrada / Cole aqui")
            file_input = gr.File(file_types=[".txt"], label="Ou carregue um arquivo .txt")
            max_len = gr.Slider(minimum=50, maximum=512, value=150, step=10, label="Tamanho máximo do resumo")
            summarize_btn = gr.Button("Summarize")
        with gr.Column(scale=2):
            output = gr.Textbox(label="Resumo", lines=12)

    def run(text, file, max_len):
        if file:
            text = file_to_text(file)
        return summarize_text(text, max_length=int(max_len))

    summarize_btn.click(run, inputs=[input_text, file_input, max_len], outputs=[output])


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
