FROM python:3.12-slim

# NEXO v2026 - Motor de Decisão Autônomo
LABEL maintainer="NEXO-MAESTRO"
LABEL description="NEXO v2026 - Bot Engenheiro com ciclo Planejar→Agir→Observar"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git \
    wget \
    curl \
    gnupg \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome (para Playwright)
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Criar diretórios necessários
RUN mkdir -p /app/data /app/logs

# Instalar dependências do Python PRIMEIRO
COPY requirements.txt .
RUN pip install --no-cache-dir --no-deps -r requirements.txt || pip install -r requirements.txt

# Copiar código da aplicação
COPY . .

# Auto-migração de ambiente (detecta incompatibilidades e corrige)
RUN python /app/nexo_migration.py || true

# Auto-validação e reparação antes de iniciar
RUN python /app/auto_validator.py || true

ENV PORT=7860
EXPOSE 7860

# CMD que executa auto-migração + validação + aplicação
CMD ["sh", "-c", "python /app/nexo_migration.py && python /app/auto_validator.py && streamlit run app.py --server.port 7860"]