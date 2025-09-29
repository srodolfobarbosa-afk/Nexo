Segurança e configuração de chaves (guia)
=====================================

ATENÇÃO: você colou várias chaves/segredos publicamente. Considere todas COMPROMETIDAS e gere novas chaves (rotate) imediatamente.

O que eu NÃO farei
- Não vou salvar nem commitar nenhuma chave secreta que você colou aqui.
- Não irei configurar variáveis de ambiente com valores reais no repositório.

O que eu faço agora
- Forneci este guia e um script auxiliar que você pode executar localmente para adicionar secrets no GitHub e no Vercel usando suas CLIs. Você controla as chaves no seu ambiente.

Passo 1 — Rotacione as chaves expostas
- Acesse os painéis das plataformas (Vercel, Supabase, OpenAI, Google Cloud, GitHub) e gere novas chaves/segredos. Revoke/disable as chaves que foram expostas.

Passo 2 — Crie um arquivo `.env` local (não commitar)
1. Crie um `.env` a partir de `.env.example` e preencha com suas chaves locais.

   cp .env.example .env
   # então edite .env e adicione suas chaves (LOCAL apenas)

2. Proteja o arquivo e não o comite:

   chmod 600 .env
   echo ".env" >> .gitignore

Passo 3 — Adicionar secrets ao GitHub (repositório)
Recomendado: Use GitHub Actions secrets (ou o GitHub Secrets no repo/org).

Usando GitHub CLI (gh):

  gh secret set SUPABASE_URL --body "<your_supabase_url_here>"
  gh secret set SUPABASE_KEY --body "<your_supabase_key_here>"
  gh secret set OPENAI_API_KEY --body "<your_openai_key_here>"
  gh secret set GEMINI_API_KEY --body "<your_gemini_key_here>"
  gh secret set VERCEL_TOKEN --body "<your_vercel_token_here>"

Passo 4 — Adicionar variáveis no Vercel (projeto)
Instale/verifique o Vercel CLI (https://vercel.com/docs/cli).

  vercel login
  vercel env add SUPABASE_URL production
  vercel env add SUPABASE_KEY production
  vercel env add OPENAI_API_KEY production
  vercel env add GEMINI_API_KEY production

Quando solicitado, cole o valor. Você também pode usar `vercel env pull` para baixar variáveis de ambiente para um `.env` local (cuidado ao compartilhar).

Passo 5 — Uso local e CI
- Localmente: carregue com `source .env` (ou use python-dotenv no seu app).
- Em CI: configure os secrets no provedor (GitHub Actions, Render, Vercel). Nunca coloque secrets em arquivos commitados.

Script auxiliar (opcional)
- Há um script em `scripts/add_secrets.sh` que chama `gh secret set` e `vercel env add` lendo valores do ambiente local. Execute-o localmente **após** exportar as variáveis no seu terminal (ex.: `export SUPABASE_URL=...`). O script não armazena keys.

Remediação se já cometeu as chaves
- Se você acidentalmente cometeu chaves, faça o seguinte rápido:
  1) Rotate/revoke as keys na plataforma (essencial)
  2) Remova do histórico git (BFG ou git filter-repo) e force push — mas mesmo assim as chaves já podem ter sido copiadas, então rotate é obrigatório.

Se quiser eu posso:
- Gerar o script `scripts/add_secrets.sh` (não recebe nem salva keys). Você roda localmente. (Posso adicionar agora.)
- Explicar como criar GitHub Actions que usam os secrets para deploy.
