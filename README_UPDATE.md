# Atualização do Projeto Nexo

## Passo 1: Configurar o ambiente
Copie o arquivo `.env.example` para `.env` e preencha suas chaves reais.

```bash
cp .env.example .env
nano .env
```

## Passo 2: Instalar dependências
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Passo 3: Rodar localmente
```bash
bash start.sh
```

## Passo 4: Testar
```bash
pytest tests/
```

## Passo 5: Deploy Automático
- O GitHub Actions (`.github/workflows/auto-deploy.yml`) já está configurado.
- A cada `git push` na branch `main`, os testes serão executados e o deploy preparado.
