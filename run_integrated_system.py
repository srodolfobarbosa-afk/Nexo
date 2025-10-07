#!/usr/bin/env python3
"""
Script para executar o Sistema de Comunicação Integrada
Manus + Nexo + Usuário via Telegram
"""

import logging
import os
import sys

from dotenv import load_dotenv

# Adicionar o diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Carregar variáveis de ambiente
load_dotenv()

# Segurança: exigir JWT_SECRET forte em ambientes onde USE_SUPABASE_AUTH=1
jwt_secret = os.environ.get("JWT_SECRET")
use_supabase_auth = os.environ.get("USE_SUPABASE_AUTH", "0")
if use_supabase_auth in ("1", "true", "True"):
    if not jwt_secret or jwt_secret in ("change_this_secret", "default_jwt_secret", ""):
        print(
            "❌ JWT_SECRET ausente ou padrão detectado. Defina uma chave forte em .env ou nas variáveis de ambiente antes de iniciar em produção."
        )
        sys.exit(2)

# Configurar logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


def main():
    """Função principal para executar o sistema integrado"""

    # Verificar configurações necessárias
    bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    if not bot_token:
        print("❌ TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
        print("📝 Configure o token do bot no Render ou no arquivo .env")
        return

    nexo_url = os.environ.get("NEXO_URL", "https://nexo-kh57.onrender.com")
    manus_api_url = os.environ.get("MANUS_API_URL", "https://api.manus.im")

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
