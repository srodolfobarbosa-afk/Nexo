# 📘 Plano de Atualização do Projeto Nexo

Este documento descreve todas as atualizações necessárias para que o projeto **Nexo** funcione de forma estável, com autonomia, memória, proatividade e interface funcional.

---

## 🔍 Diagnóstico Atual

1. **Funcionalidade mínima incompleta**
   - Rotas como `/agents`, `/missions`, `/bank` não estão ativas ou retornam erro.
   - Sem interatividade no frontend.

2. **Erros de backend/importação**
   - Problemas com módulos não encontrados (`No module named 'agentes.NexoGenesis'`).
   - Estrutura de diretórios inconsistente.

3. **Configuração de `.env` incorreta**
   - Uso de `export`, variáveis mal formatadas.

4. **Sem testes automatizados**
   - Não existe cobertura mínima de rotas.

5. **Deploy inconsistente**
   - Start Command do Render não configurado corretamente.

6. **Memória e persistência**
   - Supabase presente, mas sem integração sólida (agentes, missões, logs).

7. **Frontend limitado**
   - Apenas estático, sem dashboard interativo.

---

## 🛠 Plano de Atualização

### Fase 1 — Organizar Backend
- [ ] Adicionar `__init__.py` em todas as pastas de módulos.
- [ ] Corrigir imports (`agentes.NexoGenesis`, etc).
- [ ] Corrigir `.env` → usar `KEY=value`, sem `export`.
- [ ] Adicionar rota `/status` para health-check.

### Fase 2 — Implementar Funcionalidades Principais
- [ ] Criar rotas REST:
  - `POST /chat`
  - `GET/POST /agents`
  - `GET/POST /missions`
  - `GET/POST /bank/transactions`
- [ ] Conectar Supabase para salvar agentes, missões, banco, logs.

### Fase 3 — Auto-Construção & Memória
- [ ] Implementar pipeline `Architect → Coder → Reviewer → Deployer`.
- [ ] Persistir logs e decisões no Supabase.
- [ ] Reuso de memória em tarefas semelhantes.

### Fase 4 — Testes & Deploy Automático
- [ ] Criar testes unitários e de integração.
- [ ] Adicionar workflow GitHub Actions (`.github/workflows/auto-deploy.yml`).
- [ ] Configurar Start Command no Render (`gunicorn -w 4 -k uvicorn.workers.UvicornWorker app:app`).

### Fase 5 — Frontend Interativo
- [ ] Criar dashboard (Chat, Agentes, Missões, Banco, Logs).
- [ ] Implementar login/autenticação (Firebase Auth).
- [ ] Streaming de respostas no chat.

### Fase 6 — Documentação & Qualidade
- [ ] Atualizar `README.md` com setup, rotas e deploy.
- [ ] Adicionar ADRs (registros de decisão de arquitetura).
- [ ] Criar template de Pull Request.

### Fase 7 — Autonomia Real
- [ ] Aprendizado contínuo com logs do Supabase.
- [ ] Correção automática em caso de erro (rollback).
- [ ] Sugestão de melhorias proativas.

---

## 📊 Priorização (7 dias)
1. Corrigir `.env` e estrutura de imports.
2. Adicionar rotas REST principais.
3. Conectar Supabase (persistência mínima).
4. Configurar deploy automático (GitHub Actions + Render).
5. Criar testes básicos de rotas.
6. Adicionar dashboard simples.

---

## ✅ Critérios de Aceite
- `/status` responde `{"status":"ok"}`.
- Criar agente → salvo no Supabase.
- Criar missão → salva no Supabase.
- Registrar transação → refletida no banco.
- Deploy automático funcionando.
- Testes passando no GitHub Actions.
- Dashboard funcional com login.

---

## 🔐 Observações Importantes
- Nunca versionar `.env` no GitHub.
- Usar Secrets no Render e GitHub.
- Sempre testar em staging antes de produção.
