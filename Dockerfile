FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# install system deps
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# copy only requirements first for better caching
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy the rest of the source
COPY . /app

EXPOSE 8000

# default envs (override in production or with secrets manager)
ENV FLASK_ENV=production
ENV START_MISSION_RUNNER=true

# recommended gunicorn command; production should provide env vars and secrets
CMD ["gunicorn", "src.ws_server:app", "--bind", "0.0.0.0:8000", "--workers", "1", "--timeout", "120"]
