#!/usr/bin/env python3
"""
Script para executar o Bot do Telegram do Nexo
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Função principal para executar o bot"""

    # Verificar se o token está configurado
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
        print("📝 Configure o token do bot no Render ou no arquivo .env")
        return

    print("🤖 Iniciando Nexo Telegram Bot...")
    print(
        f"🔗 Conectando ao Nexo em: {os.environ.get('NEXO_URL', 'https://nexo-kh57.onrender.com')}"
    )

    try:
        # Importar e executar o bot
        from telegram_bot import main as bot_main

        bot_main()
    except ImportError as e:
        print(f"❌ Erro ao importar telegram_bot: {e}")
        print("📦 Verifique se pyTelegramBotAPI está instalado")
    except Exception as e:
        print(f"❌ Erro ao executar o bot: {e}")
        logging.error(f"Erro no bot: {e}")


if __name__ == "__main__":
    main()
