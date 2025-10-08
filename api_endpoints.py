"""
Endpoints de API para o Nexo - Comunicação com Bot do Telegram
"""

import logging
from datetime import datetime

import ollama
from dotenv import load_dotenv
from flask import jsonify, request

# Importar módulos do Nexo
try:
    from agentes.NexoGenesis import NexoGenesisAgent
except ImportError:
    # Fallback se o módulo não estiver disponível
    NexoGenesisAgent = None

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NexoAPI:
    def __init__(self):
        self.nexo_genesis = None
        self.ollama_client = None
        self.initialize_ollama()
        self.initialize_nexo()

    def initialize_ollama(self):
        try:
            self.ollama_client = ollama.Client()
            logger.info("Cliente Ollama inicializado com sucesso!")
        except Exception as e:
            logger.error(f"Erro ao inicializar Ollama: {e}")

    def initialize_nexo(self):
        """Inicializar o Nexo Genesis"""
        try:
            if NexoGenesisAgent:
                self.nexo_genesis = NexoGenesisAgent()
                logger.info("Nexo Genesis inicializado com sucesso")
            else:
                logger.warning("NexoGenesis não disponível, usando fallback")
        except Exception as e:
            logger.error(f"Erro ao inicializar Nexo Genesis: {e}")

    def process_message(self, message_data):
        """Processar mensagem recebida do Telegram"""
        try:
            message = message_data.get("message", "")
            user_id = message_data.get("user_id", "")
            source = message_data.get("source", "unknown")

            logger.info(
                f"Processando mensagem de {user_id} via {source}: {message[:50]}..."
            )

            llama_response = None
            if self.ollama_client and message:
                try:
                    chat_response = self.ollama_client.chat(
                        model="llama2", messages=[{"role": "user", "content": message}]
                    )
                    llama_response = chat_response["message"]["content"]
                except Exception as e:
                    logger.warning(f"Erro ao gerar resposta com Llama: {e}")

            # Se o Nexo Genesis estiver disponível, usar ele
            if self.nexo_genesis:
                response = self.nexo_genesis.processar_mensagem(message, user_id)
            elif llama_response:
                response = f"[Llama] {llama_response}"
            else:
                # Fallback: resposta simples
                response = self.generate_fallback_response(message)

            return {
                "success": True,
                "response": response,
                "timestamp": datetime.now().isoformat(),
                "processed_by": (
                    "nexo_genesis"
                    if self.nexo_genesis
                    else ("llama" if llama_response else "fallback")
                ),
            }

        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Desculpe, ocorreu um erro interno. Tente novamente.",
            }

    def generate_fallback_response(self, message):
        """Gerar resposta de fallback quando o Nexo Genesis não estiver disponível"""
        message_lower = message.lower()

        # Respostas baseadas em palavras-chave
        if any(word in message_lower for word in ["olá", "oi", "hello", "hi"]):
            return "Olá! Sou o Nexo, seu assistente de IA. Como posso ajudá-lo hoje?"

        elif any(word in message_lower for word in ["ajuda", "help", "socorro"]):
            return """
🤖 **Nexo - Assistente de IA Autônomo**

Posso ajudá-lo com:
• Análise e pesquisa de informações
• Criação de conteúdo e documentos
• Automação de tarefas
• Gerenciamento de projetos
• Integração com APIs e serviços

Envie sua solicitação e eu processarei através do sistema Nexo!
            """

        elif any(word in message_lower for word in ["status", "funcionando"]):
            return f"✅ Sistema Nexo operacional! Timestamp: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"

        elif any(word in message_lower for word in ["criar", "gerar", "desenvolver"]):
            return """
🛠️ **Capacidades de Criação do Nexo:**

Posso criar:
• Documentos e relatórios
• Códigos e scripts
• Planos e estratégias
• Análises e pesquisas
• Automações e workflows

Descreva o que você precisa criar e eu ajudarei!
            """

        elif any(word in message_lower for word in ["automatizar", "automação"]):
            return """
⚙️ **Automação com Nexo:**

Posso automatizar:
• Processos repetitivos
• Coleta de dados
• Geração de relatórios
• Integração entre sistemas
• Workflows de negócio

Conte-me sobre o processo que deseja automatizar!
            """

        else:
            return f"""
🤖 **Nexo processou sua mensagem:**

"{message}"

Atualmente operando em modo básico. Para funcionalidades completas, o sistema Nexo Genesis está sendo inicializado.

**Posso ajudar com:**
• Análise de informações
• Criação de conteúdo
• Automação de tarefas
• Pesquisa e desenvolvimento

Como posso ser mais específico em ajudá-lo?
            """


# Instância global da API
nexo_api = NexoAPI()


def register_api_routes(app):
    """Registrar rotas da API no Flask app"""

    @app.route("/api/chat", methods=["POST"])
    def chat_endpoint():
        """Endpoint para receber mensagens do bot do Telegram"""
        try:
            data = request.get_json()

            if not data or "message" not in data:
                return (
                    jsonify({"success": False, "error": "Mensagem não fornecida"}),
                    400,
                )

            # Processar mensagem
            result = nexo_api.process_message(data)

            return jsonify(result)

        except Exception as e:
            logger.error(f"Erro no endpoint de chat: {e}")
            return jsonify({"success": False, "error": "Erro interno do servidor"}), 500

    @app.route("/health", methods=["GET"])
    def health_check():
        """Endpoint de verificação de saúde"""
        return jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now().isoformat(),
                "nexo_genesis_available": nexo_api.nexo_genesis is not None,
            }
        )

    @app.route("/api/status", methods=["GET"])
    def status_endpoint():
        """Endpoint de status detalhado"""
        return jsonify(
            {
                "nexo_status": "operational",
                "nexo_genesis_available": nexo_api.nexo_genesis is not None,
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0",
                "capabilities": [
                    "chat_processing",
                    "telegram_integration",
                    "autonomous_operation",
                    "api_integration",
                ],
            }
        )

    @app.route("/api/capabilities", methods=["GET"])
    def capabilities_endpoint():
        """Endpoint para listar capacidades do Nexo"""
        return jsonify(
            {
                "capabilities": {
                    "analysis": "Análise de dados e informações",
                    "content_creation": "Criação de conteúdo e documentos",
                    "automation": "Automação de tarefas e processos",
                    "research": "Pesquisa e coleta de informações",
                    "integration": "Integração com APIs e serviços",
                    "project_management": "Gerenciamento de projetos",
                    "autonomous_operation": "Operação autônoma e proativa",
                },
                "integrations": [
                    "telegram_bot",
                    "supabase_memory",
                    "openai_api",
                    "gemini_api",
                    "web_scraping",
                    "api_calls",
                ],
                "status": "active",
            }
        )

    logger.info("Rotas da API registradas com sucesso")
