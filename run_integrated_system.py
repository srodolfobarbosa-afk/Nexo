#!/usr/bin/env python3
"""
Script para executar o Sistema de Comunicação Integrada
Manus + Nexo + Usuário via Telegram
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    """Função principal para executar o sistema integrado"""
    
    # Verificar configurações necessárias
    bot_token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
        print("📝 Configure o token do bot no Render ou no arquivo .env")
        return
    
    nexo_url = os.environ.get('NEXO_URL', 'https://nexo-kh57.onrender.com')
    manus_api_url = os.environ.get('MANUS_API_URL', 'https://api.manus.im')
    
    print("🌐 Iniciando Sistema de Comunicação Integrada...")
    print("🤖 Manus + 🔷 Nexo + 👤 Usuário")
    print(f"🔗 Nexo URL: {nexo_url}")
    print(f"🔗 Manus API: {manus_api_url}")
    print("👤 Usuário autorizado: 8016202357")
    
    try:
        # Importar e executar o sistema integrado
        from integrated_communication import main as integrated_main
        integrated_main()
    except ImportError as e:
        print(f"❌ Erro ao importar sistema integrado: {e}")
        print("📦 Verifique se todas as dependências estão instaladas")
    except Exception as e:
        print(f"❌ Erro ao executar o sistema: {e}")
        logging.error(f"Erro no sistema integrado: {e}")

if __name__ == "__main__":
    main()
