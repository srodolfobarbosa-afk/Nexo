#!/usr/bin/env python3
"""
Bot do Telegram para o Nexo - Sistema de Comunicação Independente
Permite acesso direto ao Nexo através do Telegram, otimizando o uso de créditos
"""

import logging
import os
from datetime import datetime

import requests
import telebot
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Token do bot do Telegram
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    logger.error("TELEGRAM_BOT_TOKEN não encontrado nas variáveis de ambiente")
    exit(1)

# Configurações do Nexo
NEXO_URL = os.environ.get("NEXO_URL", "https://nexo-kh57.onrender.com")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# Inicializar bot
bot = telebot.TeleBot(BOT_TOKEN)

# Armazenar contexto de conversas
user_contexts = {}


class NexoTelegramBot:
    def __init__(self):
        self.authorized_users = set()
        self.load_authorized_users()

    def load_authorized_users(self):
        """Carrega usuários autorizados (implementar com Supabase posteriormente)"""
        # Por enquanto, permitir qualquer usuário
        pass

    def is_authorized(self, user_id):
        """Verifica se o usuário está autorizado"""
        # Por enquanto, autorizar todos os usuários
        return True

    def call_nexo_api(self, message, user_id):
        """Chama a API do Nexo para processar a mensagem"""
        try:
            # Preparar dados para envio ao Nexo
            data = {
                "message": message,
                "user_id": str(user_id),
                "timestamp": datetime.now().isoformat(),
                "source": "telegram",
            }

            # Fazer requisição para o Nexo
            response = requests.post(
                f"{NEXO_URL}/api/chat",
                json=data,
                headers={"Content-Type": "application/json"},
                timeout=30,
            )

            if response.status_code == 200:
                return response.json().get("response", "Resposta recebida do Nexo")
            else:
                return f"Erro na comunicação com o Nexo: {response.status_code}"

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao chamar API do Nexo: {e}")
            return "Desculpe, não consegui me conectar ao Nexo no momento. Tente novamente em alguns instantes."

    def get_user_context(self, user_id):
        """Obtém o contexto do usuário"""
        if user_id not in user_contexts:
            user_contexts[user_id] = {"messages": [], "last_activity": datetime.now()}
        return user_contexts[user_id]

    def update_user_context(self, user_id, message, response):
        """Atualiza o contexto do usuário"""
        context = self.get_user_context(user_id)
        context["messages"].append(
            {"user": message, "nexo": response, "timestamp": datetime.now().isoformat()}
        )
        context["last_activity"] = datetime.now()

        # Manter apenas as últimas 10 mensagens para economizar memória
        if len(context["messages"]) > 10:
            context["messages"] = context["messages"][-10:]


nexo_bot = NexoTelegramBot()


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """Mensagem de boas-vindas"""
    user_id = message.from_user.id

    if not nexo_bot.is_authorized(user_id):
        bot.reply_to(
            message, "❌ Acesso não autorizado. Entre em contato com o administrador."
        )
        return

    welcome_text = """
🤖 **Bem-vindo ao Nexo Bot!**

Sou seu assistente de IA autônomo, conectado ao sistema Nexo. Posso ajudá-lo com:

🔹 **Análise e pesquisa** de informações
🔹 **Criação de conteúdo** e documentos
🔹 **Automação de tarefas** repetitivas
🔹 **Gerenciamento de projetos** e workflows
🔹 **Integração com APIs** e serviços externos

**Comandos disponíveis:**
/help - Mostrar ajuda
/status - Status do sistema
/context - Ver contexto da conversa
/clear - Limpar contexto

💡 **Dica:** Envie qualquer mensagem e eu processarei através do Nexo!
    """

    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")


@bot.message_handler(commands=["help"])
def send_help(message):
    """Mensagem de ajuda"""
    help_text = """
🆘 **Ajuda do Nexo Bot**

**Como usar:**
- Envie qualquer mensagem e eu processarei através do sistema Nexo
- Use comandos para funcionalidades específicas

**Comandos disponíveis:**
/start - Iniciar o bot
/help - Mostrar esta ajuda
/status - Verificar status do sistema
/context - Ver histórico da conversa
/clear - Limpar contexto da conversa

**Exemplos de uso:**
- "Analise o mercado de IA em 2024"
- "Crie um plano de marketing para startup"
- "Pesquise sobre tendências tecnológicas"
- "Automatize processo de vendas"

🔧 **Suporte:** Este bot está conectado ao sistema Nexo para operação autônoma e eficiente.
    """

    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")


@bot.message_handler(commands=["status"])
def send_status(message):
    """Verificar status do sistema"""
    try:
        # Verificar conectividade com o Nexo
        response = requests.get(f"{NEXO_URL}/health", timeout=10)
        if response.status_code == 200:
            status = "🟢 Online"
        else:
            status = "🟡 Parcialmente disponível"
    except:
        status = "🔴 Offline"

    status_text = f"""
📊 **Status do Sistema**

**Nexo:** {status}
**Bot:** 🟢 Online
**Última atualização:** {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}

**Estatísticas:**
- Usuários ativos: {len(user_contexts)}
- Uptime: Desde o último deploy
    """

    bot.send_message(message.chat.id, status_text, parse_mode="Markdown")


@bot.message_handler(commands=["context"])
def send_context(message):
    """Mostrar contexto da conversa"""
    user_id = message.from_user.id
    context = nexo_bot.get_user_context(user_id)

    if not context["messages"]:
        bot.send_message(message.chat.id, "📝 Nenhuma conversa registrada ainda.")
        return

    context_text = "📝 **Contexto da Conversa:**\n\n"
    for i, msg in enumerate(context["messages"][-5:], 1):  # Últimas 5 mensagens
        context_text += f"**{i}.** Você: {msg['user'][:50]}...\n"
        context_text += f"**Nexo:** {msg['nexo'][:50]}...\n\n"

    bot.send_message(message.chat.id, context_text, parse_mode="Markdown")


@bot.message_handler(commands=["clear"])
def clear_context(message):
    """Limpar contexto da conversa"""
    user_id = message.from_user.id
    if user_id in user_contexts:
        del user_contexts[user_id]

    bot.send_message(message.chat.id, "🗑️ Contexto da conversa limpo!")


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Processar mensagens gerais através do Nexo"""
    user_id = message.from_user.id

    if not nexo_bot.is_authorized(user_id):
        bot.reply_to(message, "❌ Acesso não autorizado.")
        return

    # Mostrar que está processando
    bot.send_chat_action(message.chat.id, "typing")

    try:
        # Processar mensagem através do Nexo
        response = nexo_bot.call_nexo_api(message.text, user_id)

        # Atualizar contexto
        nexo_bot.update_user_context(user_id, message.text, response)

        # Enviar resposta
        bot.send_message(message.chat.id, response, parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Ocorreu um erro ao processar sua mensagem. Tente novamente.",
        )


def main():
    """Função principal"""
    logger.info("Iniciando Nexo Telegram Bot...")

    # Verificar configurações
    if not BOT_TOKEN:
        logger.error("Token do bot não configurado")
        return

    logger.info(f"Bot configurado para conectar ao Nexo em: {NEXO_URL}")

    # Iniciar polling
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Erro no bot: {e}")


if __name__ == "__main__":
    main()
