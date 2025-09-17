#!/usr/bin/env python3
"""
Sistema de Comunicação Integrada - Manus + Nexo + Usuário
Permite comunicação tripartite através do Telegram
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv
import telebot
from telebot import types

load_dotenv()

# Configuração
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
MANUS_API_URL = os.environ.get('MANUS_API_URL', 'https://api.manus.im')
NEXO_URL = os.environ.get('NEXO_URL', 'https://nexo-kh57.onrender.com')
AUTHORIZED_USER_ID = 8016202357  # Seu Chat ID

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Inicializar bot
bot = telebot.TeleBot(BOT_TOKEN)

class IntegratedCommunicationSystem:
    def __init__(self):
        self.conversation_mode = "normal"  # normal, integrated, manus_only, nexo_only
        self.conversation_history = []
        self.active_agents = {"manus": False, "nexo": True}
        
    def set_conversation_mode(self, mode: str):
        """Define o modo de conversa"""
        valid_modes = ["normal", "integrated", "manus_only", "nexo_only"]
        if mode in valid_modes:
            self.conversation_mode = mode
            return True
        return False
    
    def call_manus_api(self, message: str, context: List[Dict] = None) -> str:
        """Chama a API do Manus para processar mensagem"""
        try:
            # Importar e usar a integração com Manus
            from manus_integration import call_manus_api
            
            response = call_manus_api(message, context)
            return f"🤖 **Manus:** {response}"
            
        except Exception as e:
            logger.error(f"Erro ao chamar API do Manus: {e}")
            return "❌ Erro ao conectar com Manus"
    
    def call_nexo_api(self, message: str, context: List[Dict] = None) -> str:
        """Chama a API do Nexo para processar mensagem"""
        try:
            data = {
                'message': message,
                'user_id': str(AUTHORIZED_USER_ID),
                'timestamp': datetime.now().isoformat(),
                'source': 'integrated_communication',
                'context': context or []
            }
            
            response = requests.post(
                f"{NEXO_URL}/api/chat",
                json=data,
                headers={'Content-Type': 'application/json'},
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return f"🔷 **Nexo:** {result.get('response', 'Resposta processada')}"
            else:
                return f"❌ Erro na comunicação com Nexo: {response.status_code}"
                
        except Exception as e:
            logger.error(f"Erro ao chamar API do Nexo: {e}")
            return "❌ Erro ao conectar com Nexo"
    
    def process_integrated_message(self, message: str) -> List[str]:
        """Processa mensagem no modo integrado (ambos os agentes respondem)"""
        responses = []
        
        # Adicionar mensagem ao histórico
        self.conversation_history.append({
            "user": message,
            "timestamp": datetime.now().isoformat()
        })
        
        # Obter contexto recente
        recent_context = self.conversation_history[-5:] if len(self.conversation_history) > 1 else []
        
        if self.conversation_mode == "integrated":
            # Ambos os agentes respondem
            if self.active_agents["nexo"]:
                nexo_response = self.call_nexo_api(message, recent_context)
                responses.append(nexo_response)
            
            if self.active_agents["manus"]:
                manus_response = self.call_manus_api(message, recent_context)
                responses.append(manus_response)
                
        elif self.conversation_mode == "nexo_only":
            if self.active_agents["nexo"]:
                nexo_response = self.call_nexo_api(message, recent_context)
                responses.append(nexo_response)
                
        elif self.conversation_mode == "manus_only":
            if self.active_agents["manus"]:
                manus_response = self.call_manus_api(message, recent_context)
                responses.append(manus_response)
                
        else:  # normal mode - apenas Nexo por padrão
            if self.active_agents["nexo"]:
                nexo_response = self.call_nexo_api(message, recent_context)
                responses.append(nexo_response)
        
        # Adicionar respostas ao histórico
        for response in responses:
            self.conversation_history.append({
                "agent_response": response,
                "timestamp": datetime.now().isoformat()
            })
        
        return responses
    
    def get_status(self) -> str:
        """Retorna status do sistema"""
        status_text = f"""
🔄 **Status do Sistema de Comunicação Integrada**

**Modo atual:** {self.conversation_mode}
**Agentes ativos:**
- Nexo: {'✅' if self.active_agents['nexo'] else '❌'}
- Manus: {'✅' if self.active_agents['manus'] else '❌'}

**Histórico:** {len(self.conversation_history)} mensagens
**Última atividade:** {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}

**Modos disponíveis:**
- `normal` - Apenas Nexo responde
- `integrated` - Ambos respondem
- `nexo_only` - Apenas Nexo
- `manus_only` - Apenas Manus
        """
        return status_text

# Instância global do sistema
comm_system = IntegratedCommunicationSystem()

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Mensagem de boas-vindas do sistema integrado"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "❌ Acesso não autorizado.")
        return
    
    welcome_text = """
🌐 **Sistema de Comunicação Integrada**
**Manus + Nexo + Você**

Agora você pode conversar com ambos os agentes de IA simultaneamente!

**Comandos disponíveis:**
/mode - Alterar modo de conversa
/status - Ver status do sistema
/agents - Ativar/desativar agentes
/history - Ver histórico recente
/clear - Limpar histórico
/help - Mostrar ajuda

**Modos de conversa:**
🔹 **Normal** - Apenas Nexo responde
🔹 **Integrado** - Ambos respondem
🔹 **Nexo Only** - Apenas Nexo
🔹 **Manus Only** - Apenas Manus

💡 Envie qualquer mensagem para começar!
    """
    
    bot.send_message(message.chat.id, welcome_text, parse_mode="Markdown")

@bot.message_handler(commands=['mode'])
def change_mode(message):
    """Alterar modo de conversa"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    # Criar teclado inline para seleção de modo
    markup = types.InlineKeyboardMarkup()
    markup.row(
        types.InlineKeyboardButton("🔹 Normal", callback_data="mode_normal"),
        types.InlineKeyboardButton("🌐 Integrado", callback_data="mode_integrated")
    )
    markup.row(
        types.InlineKeyboardButton("🔷 Nexo Only", callback_data="mode_nexo_only"),
        types.InlineKeyboardButton("🤖 Manus Only", callback_data="mode_manus_only")
    )
    
    bot.send_message(
        message.chat.id,
        f"**Modo atual:** {comm_system.conversation_mode}\n\nEscolha o novo modo:",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('mode_'))
def handle_mode_change(call):
    """Processar mudança de modo"""
    if call.from_user.id != AUTHORIZED_USER_ID:
        return
    
    mode = call.data.replace('mode_', '')
    if comm_system.set_conversation_mode(mode):
        bot.edit_message_text(
            f"✅ Modo alterado para: **{mode}**",
            call.message.chat.id,
            call.message.message_id,
            parse_mode="Markdown"
        )
    else:
        bot.edit_message_text(
            "❌ Modo inválido",
            call.message.chat.id,
            call.message.message_id
        )

@bot.message_handler(commands=['status'])
def send_status(message):
    """Mostrar status do sistema"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    status = comm_system.get_status()
    bot.send_message(message.chat.id, status, parse_mode="Markdown")

@bot.message_handler(commands=['agents'])
def manage_agents(message):
    """Gerenciar agentes ativos"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    markup = types.InlineKeyboardMarkup()
    nexo_status = "✅" if comm_system.active_agents["nexo"] else "❌"
    manus_status = "✅" if comm_system.active_agents["manus"] else "❌"
    
    markup.row(
        types.InlineKeyboardButton(f"Nexo {nexo_status}", callback_data="toggle_nexo"),
        types.InlineKeyboardButton(f"Manus {manus_status}", callback_data="toggle_manus")
    )
    
    bot.send_message(
        message.chat.id,
        "**Gerenciar Agentes Ativos:**\nClique para ativar/desativar",
        reply_markup=markup,
        parse_mode="Markdown"
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('toggle_'))
def handle_agent_toggle(call):
    """Processar ativação/desativação de agentes"""
    if call.from_user.id != AUTHORIZED_USER_ID:
        return
    
    agent = call.data.replace('toggle_', '')
    if agent in comm_system.active_agents:
        comm_system.active_agents[agent] = not comm_system.active_agents[agent]
        status = "ativado" if comm_system.active_agents[agent] else "desativado"
        bot.edit_message_text(
            f"✅ {agent.title()} {status}",
            call.message.chat.id,
            call.message.message_id
        )

@bot.message_handler(commands=['history'])
def show_history(message):
    """Mostrar histórico recente"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    if not comm_system.conversation_history:
        bot.send_message(message.chat.id, "📝 Nenhum histórico disponível")
        return
    
    history_text = "📝 **Histórico Recente (últimas 5 mensagens):**\n\n"
    recent = comm_system.conversation_history[-10:]
    
    for i, entry in enumerate(recent, 1):
        if "user" in entry:
            history_text += f"**{i}.** Você: {entry['user'][:50]}...\n"
        elif "agent_response" in entry:
            history_text += f"**Resposta:** {entry['agent_response'][:100]}...\n\n"
    
    bot.send_message(message.chat.id, history_text, parse_mode="Markdown")

@bot.message_handler(commands=['clear'])
def clear_history(message):
    """Limpar histórico"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    comm_system.conversation_history = []
    bot.send_message(message.chat.id, "🗑️ Histórico limpo!")

@bot.message_handler(commands=['help'])
def send_help(message):
    """Mostrar ajuda"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        return
    
    help_text = """
🆘 **Ajuda - Sistema de Comunicação Integrada**

**Comandos:**
/mode - Alterar modo de conversa
/status - Ver status do sistema
/agents - Ativar/desativar agentes
/history - Ver histórico recente
/clear - Limpar histórico

**Modos de Conversa:**
- **Normal:** Apenas Nexo responde
- **Integrado:** Ambos os agentes respondem
- **Nexo Only:** Apenas Nexo responde
- **Manus Only:** Apenas Manus responde

**Como usar:**
1. Escolha o modo com /mode
2. Envie sua mensagem
3. Receba respostas dos agentes ativos
4. Continue a conversa naturalmente

🔧 **Recursos:**
- Contexto persistente entre mensagens
- Histórico de conversas
- Controle individual de agentes
- Múltiplos modos de operação
    """
    
    bot.send_message(message.chat.id, help_text, parse_mode="Markdown")

@bot.message_handler(func=lambda message: True)
def handle_integrated_message(message):
    """Processar mensagens no sistema integrado"""
    if message.from_user.id != AUTHORIZED_USER_ID:
        bot.reply_to(message, "❌ Acesso não autorizado.")
        return
    
    # Mostrar que está processando
    bot.send_chat_action(message.chat.id, 'typing')
    
    try:
        # Processar mensagem através do sistema integrado
        responses = comm_system.process_integrated_message(message.text)
        
        if not responses:
            bot.send_message(message.chat.id, "⚠️ Nenhum agente ativo para processar a mensagem")
            return
        
        # Enviar cada resposta
        for response in responses:
            bot.send_message(message.chat.id, response, parse_mode="Markdown")
            
    except Exception as e:
        logger.error(f"Erro ao processar mensagem integrada: {e}")
        bot.send_message(
            message.chat.id,
            "❌ Erro ao processar mensagem. Tente novamente."
        )

def main():
    """Função principal"""
    logger.info("Iniciando Sistema de Comunicação Integrada...")
    
    if not BOT_TOKEN:
        logger.error("Token do bot não configurado")
        return
    
    logger.info(f"Sistema configurado para usuário: {AUTHORIZED_USER_ID}")
    logger.info(f"Nexo URL: {NEXO_URL}")
    logger.info(f"Manus API URL: {MANUS_API_URL}")
    
    try:
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Erro no sistema integrado: {e}")

if __name__ == "__main__":
    main()
