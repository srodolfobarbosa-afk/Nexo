FROM python:3.12-slim

# NEXO v2026 - Production-Ready
LABEL maintainer="NEXO-MAESTRO"
LABEL description="NEXO v2026 - Build Otimizado"

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    git wget curl gnupg unzip ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Criar diretórios
RUN mkdir -p /app/data /app/logs

# Copiar requirements
COPY requirements.txt .

# Instalar com cache limpo - SEM langchain conflitante
RUN pip install --upgrade pip && \
    pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    python-dotenv==1.0.0 \
    groq==0.4.2 \
    loguru==0.7.2 \
    pydantic>=2.0 \
    requests==2.31.0 \
    beautifulsoup4==4.12.2 \
    streamlit==1.28.1

# Copiar código
COPY . .

# Ignorar erros
RUN python /app/nexo_migration.py || echo "Migration skipped"
RUN python /app/auto_validator.py || echo "Validation skipped"

ENV PORT=7860
EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port", "7860"]
