# Mapa de Infraestrutura (Gratuita) — Nexo

Este arquivo descreve um desenho prático para rodar o projeto inteiro usando serviços gratuitos ou com camadas grátis. Inclui componentes, fluxos, e passos de configuração mínimos para deploy e operação.

Resumo rápido
- Frontend: Vercel (ou Render static)
- Backend/API: Render (free tier) ou Vercel Serverless Functions
- Banco: Supabase (Postgres + Auth) - plano gratuito
- Armazenamento de segredos / CI: GitHub (repos + Actions + Secrets)
- Registry de imagens: GitHub Container Registry (GHCR) — grátis por repositório
- LLMs: fallback entre OpenAI (se houver crédito), Google Gemini, e um fallback local mínimo
- Execução contínua de bots: Replit (ou Render background worker) — grátis com limites

Arquitetura proposta

[User] <--HTTPS--> [Vercel Frontend] <--HTTPS--> [API (Render / Vercel functions)]
                                     |
                                     +--> [Supabase Postgres + Auth]
                                     |
                                     +--> [GHCR images (CI build)]
                                     |
                                     +--> [LLM Providers (OpenAI/Gemini/fallback)]

Componentes e por que escolher

- Vercel: rápido para servir frontend e páginas estáticas. Deploy automático em push. Bom para interfaces, dashboards e websockets via serverless (ou proxys).
- Render: melhor para executar processos persistentes (workers/bots) com background processes; possui integração com GitHub e suporte a processos longos.
- Supabase: Postgres gerenciado + Auth + Storage; gratuito e integra bem com frontend e backend.
- GitHub Actions + GHCR: CI para build/test e push de imagens. GHCR é grátis para repositórios públicos e tem integração nativa com Actions.
- Replit: alternativa para rodar bots 24/7 (com algumas limitações). Útil se não quiser gerenciar infra.

Fluxo de CI/CD sugerido
1. Desenvolvedor faz push para `main`.
2. GitHub Actions roda lint/tests.
3. Actions builda imagem otimizada (usa `requirements_prod.txt`) e pusha para `ghcr.io/${{ github.repository }}:${{ github.sha }}`.
4. Actions chama API do Render para disparar deploy (workflow já incluso no repositório). Alternativa: use integração GitHub-Render.

Segredos e configurações necessárias
- `SUPABASE_URL`, `SUPABASE_KEY` → armazenar no GitHub Secrets para ambiente de backend.
- `RENDER_SERVICE_ID`, `RENDER_API_TOKEN` → para acionar deploy via API (ou configure integração GitHub no painel do Render).
- `OPENAI_API_KEY`, `GOOGLE_API_KEY` → provider LLM (usar preferencialmente GitHub Secrets). Sempre tenha um fallback local.

Boas práticas para custo zero
- Separe dependências pesadas (ML) em `requirements_dev.txt` ou `requirements_clean.txt`. Use `requirements_prod.txt` para builds em CI/Render.
- Configure motores LLM em ordem de prioridade e com limites de fallback:
  1. OpenAI / paid provider (se disponível)
  2. Google Gemini (gratuito com quota)
  3. Local fallback (modo echo / regras simples) — nunca quebre sem LLM
- Use caches e limites (timeouts, retries, rate limits) para requests a APIs pagas.

Passo-a-passo rápido para montar (mínimo)
1. GitHub: push do repositório.
2. Supabase: criar projeto gratuito, copiar `SUPABASE_URL` e `SUPABASE_KEY` para GitHub Secrets.
3. Vercel: conectar repositório, configurar variáveis de ambiente (copiar `SUPABASE_*`) e deploy automático.
4. Render (opcional para backend persistente): criar serviço Python, apontar para repo ou para imagem do GHCR; configurar `render.yaml` e variáveis.
5. GitHub Actions: garantir workflow `ci.yml` (lint/test) e `render-deploy.yml` (build/push/deploy). Configurar `RENDER_*` secrets se for usar a API.

Como integrar LLMs com fallback (pseudocódigo)

1. Tente provider primário (OPENAI).
2. Se não existir key ou erro de quota, tente provider secundário (GOOGLE).
3. Se ambos falharem, use fallback local (ex.: heurística ou prompt template simples).

Exemplo de prioridade em `config`:

```json
{
  "llm_priority": ["openai", "google", "fallback_local"]
}
```

Checklist de verificação antes do deploy
- [ ] `requirements_prod.txt` presente e enxuto
- [ ] `render.yaml` ou configuração de serviço no Render pronta
- [ ] GitHub Secrets: `SUPABASE_URL`, `SUPABASE_KEY`, `RENDER_SERVICE_ID`, `RENDER_API_TOKEN`, `OPENAI_API_KEY` (opc)
- [ ] `INIT_WORKSPACE.md` atualizado com instruções (já incluso)

Próxima etapa prática
- Se quiser, começo implementando o primeiro agente funcional que:
  - persiste usuários/missões em Supabase
  - usa LLM via fallback chain
  - roda localmente ou como worker no Render/Replit

Veja `agentes/StarterAgent.py` (exemplo leve) para testar localmente sem depender de chaves.

***
Se quiser que eu já implemente o agente inicial completo, responda: "Implemente o agente". Se preferir que eu apenas desenhe um diagrama visual (Mermaid), diga "Diagrama".
