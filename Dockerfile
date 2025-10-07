FROM --platform=linux/amd64 python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# instalar dependências de sistema necessárias para compilar algumas wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar apenas requirements para cache eficiente
COPY requirements.txt /app/requirements.txt
RUN python -m pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir -r /app/requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

# runtime deps
RUN apt-get update && apt-get install -y --no-install-recommends libpq5 ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# copiar pacotes instalados do builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# copiar código
COPY . /app

EXPOSE 8000

# variáveis default (podem ser sobrescritas em produção)
ENV FLASK_ENV=production
ENV START_MISSION_RUNNER=true

USER root

# startup recomendado (override via ENTRYPOINT/CMD em produção)
CMD ["gunicorn", "src.ws_server:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120"]
