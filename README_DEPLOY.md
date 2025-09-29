# Deploy rápido: Nexo Summarization (Gradio)

Este pequeno app permite executar sumarização localmente ou em plataformas gratuitas como Hugging Face Spaces ou Replit.

Requisitos
- Um repo com este arquivo `app_hf_space.py` e `requirements_hf_space.txt`.

Opção A — Hugging Face Spaces (recomendado para UI rápida):
1. Crie uma conta em https://huggingface.co/
2. Vá em "Spaces" → "Create new Space" → escolha "Gradio" e público/privado.
3. Faça upload de `app_hf_space.py` e `requirements_hf_space.txt` no repositório da Space.
4. A Space instalará as dependências e iniciará automaticamente. Aguarde o build.

Observações:
- O modelo `google/flan-t5-small` é relativamente leve, mas ainda precisa de CPU considerável.
- Se você tiver acesso a GPU na Space, configure-a para acelerar a inferência.

Uso da Hugging Face Inference API (opcional — evita download de pesos):

- Se você quiser que a Space (ou Replit) chame a Inference API em vez de carregar pesos localmente, defina a variável de ambiente `HUGGINGFACE_API_KEY` na sua Space/Repl com sua chave de API da Hugging Face.
- Quando `HUGGINGFACE_API_KEY` estiver presente, o app fará chamadas para a API e retornará o texto gerado. Isso reduz consumo de CPU/memória local, mas consome quota da sua conta Hugging Face.

Opção B — Replit (rápido e grátis para protótipos):

Opção B — Replit (rápido e grátis para protótipos):
1. Crie um novo Repl (Python).
2. Faça upload de `app_hf_space.py` e `requirements_hf_space.txt`.
3. Em Replit, instale dependências via shell: `pip install -r requirements_hf_space.txt`.
4. Execute `python app_hf_space.py` e clique no link fornecido pelo Replit.

Limitações e dicas:
- Para produção, considere usar um backend com GPUs e um modelo maior (p.ex. flan-t5-base ou flan-t5-xl).
- Se o tempo de inicialização for alto, adicione caching do modelo ou uma página de loading.
