FROM python:3.12-slim

LABEL maintainer="NEXO-MAESTRO"

RUN apt-get update && apt-get install -y git wget curl gnupg unzip ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Force latest from git
RUN git clone https://github.com/srodolfobarbosa-afk/Nexo.git /tmp/nexo_latest && cp -r /tmp/nexo_latest/* . && rm -rf /tmp/nexo_latest

RUN mkdir -p /app/data /app/logs

COPY requirements.txt .

RUN pip install --upgrade pip && pip install --no-cache-dir fastapi==0.104.1 uvicorn==0.24.0 python-dotenv==1.0.0 groq==0.4.2 loguru==0.7.2 pydantic>=2.0 requests==2.31.0 beautifulsoup4==4.12.2 streamlit==1.28.1

COPY . .

RUN python /app/nexo_migration.py || echo "skip"
RUN python /app/auto_validator.py || echo "skip"

ENV PORT=7860
EXPOSE 7860

CMD ["streamlit", "run", "app.py", "--server.port", "7860"]
