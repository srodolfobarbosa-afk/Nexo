#!/bin/bash
# ==============================================================================
# NEXO V37.3 - Script de Inicialização
# ==============================================================================

echo "🔱 NEXO V37.3: Iniciando sistema..."

# Verifica se Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 não encontrado. Instale Python 3.11 ou superior."
    exit 1
fi

# Verifica se .env existe
if [ ! -f .env ]; then
    echo "⚠️ Arquivo .env não encontrado."
    echo "📋 Copiando .env.example para .env..."
    cp .env.example .env
    echo "✅ Arquivo .env criado. Configure suas chaves de API antes de continuar."
    echo "📝 Edite o arquivo .env e adicione sua GROQ_API_KEY"
    exit 1
fi

# Cria diretórios necessários
echo "📁 Criando diretórios..."
mkdir -p data/habilidades
mkdir -p static

# Instala dependências
echo "📦 Instalando dependências..."
pip install -r requirements.txt

# Verifica se Chrome está instalado
if ! command -v google-chrome &> /dev/null && ! command -v chromium-browser &> /dev/null; then
    echo "⚠️ Chrome/Chromium não encontrado."
    echo "💡 Para funcionalidade completa do navegador, instale:"
    echo "   Ubuntu/Debian: sudo apt-get install google-chrome-stable"
    echo "   Ou: sudo apt-get install chromium-browser"
fi

# Inicia o servidor
echo "🚀 Iniciando NEXO MAESTRO..."
python3 app.py
