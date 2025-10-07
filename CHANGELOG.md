# CHANGELOG

## 2025-10-07 — Auditoria e correções iniciais

- Ajustes para tornar a suíte de testes executável localmente (lazy imports em agentes críticos).
- Adicionado `flask-sock`, `cryptography`, `sqlalchemy` e dependências dev mínimas em `requirements_dev.txt`.
- Adicionado formatação e lint (black/isort/ruff) e configurações em `pyproject.toml`.
- Dockerfile convertido para multistage e adicionado `docker-compose.yml` para desenvolvimento local.
- Criação de workflow consolidado em `.github/workflows/consolidated-ci.yml`.
- Atualização de `README.md` com passos básicos de setup, testes e docker.
