Deploy no Render — instruções rápidas

Passos mínimos para publicar o Nexo no Render (web service):

1. Crie um novo Web Service no Render.
   - Tipo: "Web Service"
   - Ambiente: "Docker" (usando o `Dockerfile`) ou "Python" (usando `render.yaml`)

2. Se usar o modo Docker (recomendado para parity com este repositório):
   - Suba o repositório.
   - Defina a porta (Render expõe via variável $PORT — o `Dockerfile` já usa $PORT no CMD).
   - Adicione as Secrets necessárias em Settings > Environment > Environment Secrets:
     - SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY, RENDER_API_KEY (se usar API de deploy), etc.

3. Se usar o modo "Native Python" (render.yaml):
   - Render usará o `buildCommand` e `startCommand` definidos em `render.yaml`.
   - Certifique-se de adicionar as mesmas Secrets de ambiente listadas em `.env.example`.

4. Variáveis recomendadas:
   - START_MISSION_RUNNER=true
   - APP_ENV=PROD
   - SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY (quando aplicável)

5. Problemas comuns:
   - Conflito de dependências (ex.: uvicorn): alinhe `requirements.txt` e `autoconstructor/requirements.txt`.
   - Playwright precisa do passo `playwright install` no build (incluso no `render.yaml` buildCommand).
   - Se usar o modo Docker, certifique-se de que o `Dockerfile` copia os pacotes do estágio builder e o CMD usa `$PORT`.

Se quiser, eu posso:
- Criar um `service` no Render automaticamente via API (preciso das suas credenciais RENDER_API_KEY), ou
- Testar uma build Docker localmente aqui para validar rapidamente.
