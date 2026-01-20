#!/bin/bash

# NEXO v2026 - Script de Deployment Docker
# Uso: ./docker-deploy.sh [start|stop|rebuild|logs|shell]

set -e

COMMAND="${1:-start}"
CONTAINER_NAME="nexo-v2026"
IMAGE_NAME="nexo-maestro/nexo-v2026:latest"

echo "🤖 NEXO v2026 - Docker Deployment"
echo "=================================="

case "$COMMAND" in
  start)
    echo "🚀 Iniciando NEXO v2026..."
    docker-compose up -d
    echo "✅ Container iniciado!"
    echo "🌐 Acesse: http://localhost:7860"
    docker-compose logs -f
    ;;
    
  stop)
    echo "⏸️ Parando NEXO v2026..."
    docker-compose down
    echo "✅ Container parado!"
    ;;
    
  rebuild)
    echo "🔨 Reconstruindo imagem..."
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    echo "✅ Imagem reconstruída e container iniciado!"
    ;;
    
  logs)
    echo "📋 Exibindo logs..."
    docker-compose logs -f --tail=50
    ;;
    
  shell)
    echo "🐚 Abrindo shell do container..."
    docker-compose exec nexo bash
    ;;
    
  push)
    echo "📤 Fazendo push da imagem..."
    docker-compose build
    docker tag nexo-maestro/nexo-v2026:latest registry.hf.space/nexo-maestro-srodolfobarbosa:latest
    docker push registry.hf.space/nexo-maestro-srodolfobarbosa:latest
    echo "✅ Push concluído!"
    ;;
    
  test)
    echo "🧪 Testando build..."
    docker-compose build
    echo "✅ Build OK!"
    ;;
    
  *)
    echo "Uso: ./docker-deploy.sh [comando]"
    echo ""
    echo "Comandos disponíveis:"
    echo "  start   - Inicia o container"
    echo "  stop    - Para o container"
    echo "  rebuild - Reconstrói a imagem"
    echo "  logs    - Exibe logs em tempo real"
    echo "  shell   - Abre shell no container"
    echo "  push    - Faz push para HF Registry"
    echo "  test    - Testa build"
    exit 1
    ;;
esac
