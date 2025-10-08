FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# instalar dependências de sistema necessárias para compilar algumas wheels
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# copiar apenas requirements para cache eficiente
COPY requirements.txt /app/requirements.txt
COPY requirements_clean.txt /app/requirements_clean.txt
COPY requirements_prod.txt /app/requirements_prod.txt

# build arg to explicitly allow heavy installs (default: disabled)
ARG INSTALL_FULL=false

# Install Python build tools and dependencies from requirements_prod.txt by default.
# If you need to install the full/heavy requirements, pass
# --build-arg INSTALL_FULL=true to the docker build command.
RUN python -m pip install --upgrade pip setuptools wheel && \
    if [ "$INSTALL_FULL" = "true" ] && [ -f /app/requirements_full.txt ]; then \
        echo "INSTALL_FULL=true -> installing requirements_full.txt (heavy)" && \
        pip install --no-cache-dir -r /app/requirements_full.txt; \
    elif [ -f /app/requirements_prod.txt ]; then \
        echo "Installing production requirements..." && \
        pip install --no-cache-dir -r /app/requirements_prod.txt; \
    else \
        echo "No production requirements found and INSTALL_FULL not enabled. To install heavy deps, rebuild with '--build-arg INSTALL_FULL=true' or add a requirements_prod.txt." && exit 1; \
    fi && \
    # ensure pip caches/temporary files are cleaned
    python -m pip cache purge || true

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
