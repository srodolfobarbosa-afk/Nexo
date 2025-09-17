import os
import json
import logging
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class SelfCorrectionModule:
    def __init__(self, agent_name: str = "Manus"): # Alterado para Manus
        self.agent_name = agent_name
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = None
        self.initialize_supabase()
        self.error_log_table = "agent_error_log"
        self.learning_memory_table = "agent_learning_memory"

    def initialize_supabase(self):
        if not self.supabase_url or not self.supabase_key:
            logger.error("SUPABASE_URL ou SUPABASE_KEY não configurados para SelfCorrectionModule.")
            return
        try:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("Conexão com Supabase estabelecida para SelfCorrectionModule.")
            self._ensure_tables_exist()
        except Exception as e:
            logger.error(f"Erro ao conectar com Supabase para SelfCorrectionModule: {e}")

    def _ensure_tables_exist(self):
        # Em um ambiente real, estas tabelas seriam criadas via migrações.
        # Aqui, apenas logamos a intenção.
        logger.info(f"Verificando/Criando tabela: {self.error_log_table}")
        logger.info(f"Verificando/Criando tabela: {self.learning_memory_table}")

    def log_error(self, error_type: str, description: str, context: dict = None):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível logar erro.")
            return
        try:
            data, count = self.supabase.table(self.error_log_table).insert({
                "agent_name": self.agent_name,
                "error_type": error_type,
                "description": description,
                "context": json.dumps(context) if context else "{}",
                "timestamp": datetime.now().isoformat()
            }).execute()
            logger.error(f"Erro logado para {self.agent_name}: {error_type} - {description}")
        except Exception as e:
            logger.error(f"Erro ao logar erro no Supabase: {e}")

    def add_to_learning_memory(self, lesson: str, action_taken: str, effectiveness: str, context: dict = None):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível adicionar à memória de aprendizado.")
            return
        try:
            data, count = self.supabase.table(self.learning_memory_table).insert({
                "agent_name": self.agent_name,
                "lesson": lesson,
                "action_taken": action_taken,
                "effectiveness": effectiveness,
                "context": json.dumps(context) if context else "{}",
                "timestamp": datetime.now().isoformat()
            }).execute()
            logger.info(f"Lição aprendida adicionada à memória para {self.agent_name}: {lesson}")
        except Exception as e:
            logger.error(f"Erro ao adicionar lição à memória de aprendizado: {e}")

    def retrieve_learning_lessons(self, query: str = None, limit: int = 5) -> list:
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível recuperar lições.")
            return []
        try:
            # Simples recuperação. Em um sistema real, usaria embeddings para busca semântica.
            if query:
                response = self.supabase.table(self.learning_memory_table)
                .select("lesson, action_taken, effectiveness, context")
                .ilike("lesson", f"%{query}%")
                .order("timestamp", ascending=False)
                .limit(limit)
                .execute()
            else:
                response = self.supabase.table(self.learning_memory_table)
                .select("lesson, action_taken, effectiveness, context")
                .order("timestamp", ascending=False)
                .limit(limit)
                .execute()
            
            return response.data
        except Exception as e:
            logger.error(f"Erro ao recuperar lições da memória de aprendizado: {e}")
            return []

    def reflect_on_performance(self, user_feedback: str, current_context: dict = None):
        # Esta função simula a reflexão do agente sobre seu desempenho
        # Em um sistema real, isso envolveria um LLM analisando o feedback e o histórico
        logger.info(f"Iniciando auto-reflexão com base no feedback do usuário: {user_feedback}")
        
        # Exemplo de lição aprendida com base no feedback do usuário
        if "esquecer" in user_feedback.lower() or "memória" in user_feedback.lower() or "contexto" in user_feedback.lower():
            lesson = "Manter o contexto da conversa e o histórico de ações é crucial para a proatividade e a confiança do usuário."
            action = "Priorizar a recuperação e o uso do histórico de conversas e ações passadas em todas as interações futuras."
            effectiveness = "alta" # Espera-se alta eficácia se aplicado
            selfn.add_to_learning_memory(lesson, action, effectiveness, current_context)
            
        if "discurso" in user_feedback.lower() or "ação real" in user_feedback.lower() or "prático" in user_feedback.lower():
            lesson = "A proatividade deve se manifestar em ações concretas e executáveis, não apenas em planos ou promessas."
            action = "Sempre que possível, gerar código, scripts ou configurações que o usuário possa executar diretamente, ou realizar ações que avancem o projeto sem intervenção direta do usuário."
            effectiveness = "alta"
            self.add_to_learning_memory(lesson, action, effectiveness, current_context)

        logger.info("Auto-reflexão concluída. Lições adicionadas à memória de aprendizado.")

# Exemplo de uso
if __name__ == "__main__":
    # Certifique-se de que SUPABASE_URL e SUPABASE_KEY estão no seu .env
    # e que as tabelas existem ou serão criadas automaticamente pelo Supabase
    correction_module = SelfCorrectionModule()
    
    # Simular um erro
    correction_module.log_error("ContextLoss", "Perda de contexto em interação crítica", {"user_message": "...", "agent_response": "..."})
    
    # Simular feedback do usuário e reflexão
    feedback = "Você esqueceu o que conversamos! Precisa de mais ação real."
    correction_module.reflect_on_performance(feedback, {"current_task": "Implementar comunicação integrada"})
    
    # Recuperar lições aprendidas
    lessons = correction_module.retrieve_learning_lessons()
    print("\n--- Lições Aprendidas ---")
    for lesson in lessons:
        print(f"Lição: {lesson["lesson"]}\nAção: {lesson["action_taken"]}\nEficácia: {lesson["effectiveness"]}\n")

    lessons_about_context = correction_module.retrieve_learning_lessons(query="contexto")
    print("\n--- Lições sobre Contexto ---")
    for lesson in lessons_about_context:
        print(f"Lição: {lesson["lesson"]}\nAção: {lesson["action_taken"]}\nEficácia: {lesson["effectiveness"]}\n")

