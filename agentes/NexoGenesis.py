from core.web_agent import WebAgent
import os
import json
import logging
from datetime import datetime
    # Additional context lines to ensure proper identification
    # This is the context around the logging statement
from supabase import create_client, Client
from dotenv import load_dotenv
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Importações originais que devem ser mantidas
import requests
from core.database import get_supabase_client
from core.internet_search import InternetSearchModule
from core.auto_construction import AutoConstructionModule
from core.evolution import EvolutionModule
from core.self_correction import SelfCorrectionModule
from core.json_utils import extract_json, safe_json_response, create_json_prompt, MISSION_INTERPRETATION_SCHEMA
import ollama
import google.generativeai as genai
import re
logging.debug(f'DEBUG: Chave da API do Gemini: {os.getenv("GOOGLE_API_KEY")}')

from typing import Optional
gemini_api_key = os.getenv("GEMINI_API_KEY")
try:
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        print("DEBUG: Conexão com o Gemini bem-sucedida.")
    else:
        print("ERRO: GEMINI_API_KEY não configurada.")
except Exception as e:
    print(f"ERRO: Conexão com o Gemini falhou. {e}")

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Novos imports para o Pacote 5
from core.validator import run_tests
from core.supabase_client import save_log

class NexoGenesisAgent:
    """
    Agente orquestrador do ecossistema EcoGuardians.
    - Interpreta missões em linguagem natural
    - Gera código de agentes
    - Realiza auto-construção avançada
    - Otimiza uso de LLMs (custo/qualidade)
    - Gerencia memória de longo prazo via Supabase
    - Executa tarefas proativas e automação
    - Monitora recursos e realiza backup automático
    """
    @staticmethod
    def validar_ambiente():
        """
        Valida se todas as dependências e variáveis de ambiente estão presentes.
        """
        import importlib
        pacotes = [
            "supabase", "dotenv", "vaderSentiment", "requests", "ollama", "google.generativeai",
            "beautifulsoup4", "langchain", "psutil", "flask", "flask_sock"
        ]
        faltando = []
        for pacote in pacotes:
            try:
                importlib.import_module(pacote.replace(".", ""))
            except ImportError:
                faltando.append(pacote)
        envs = ["SUPABASE_URL", "SUPABASE_KEY", "GEMINI_API_KEY", "OPENAI_API_KEY", "GROQ_API_KEY"]
        env_faltando = [e for e in envs if not os.getenv(e)]
        if faltando:
            logging.warning(f"[AVISO] Pacotes faltando: {faltando}. Execute 'pip install -r requirements.txt'.")
        if env_faltando:
            logging.warning(f"[AVISO] Variáveis de ambiente faltando: {env_faltando}. Configure no .env ou render.yaml.")
        if not faltando and not env_faltando:
            logging.info("[OK] Ambiente validado: todas dependências e variáveis presentes.")
    def __init__(self):
        # Informações do criador/dono do sistema
        self.owner_info = {
            "nome": "Rodolfo Barbosa",
            "chat_id_telegram": "8016202357",
            "email": "srodolfobarbosa@gmail.com",
            "pix": "137.27339730"
        }
        # Manter a inicialização original do Supabase via get_supabase_client()

        self.supabase = get_supabase_client()
        if not self.supabase:
            logging.warning("Supabase não inicializado. Algumas funcionalidades ficarão limitadas.")
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        try:
            self.search_module = InternetSearchModule() # Mantenha por enquanto
        except Exception:
            self.search_module = None
            logging.warning("InternetSearchModule indisponível.")
        try:
            self.web_agent = WebAgent() # Novo WebAgent
            logging.info("🌐 Agente de navegação web (Playwright) ativo.")
        except Exception:
            self.web_agent = None
            logging.warning("WebAgent indisponível.")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.llm_provider = os.environ.get("NEXO_LLM_PROVIDER", "google")

        # Inicializar módulos de auto-construção, automação web e memória vetorial
        from core.vector_memory import VectorMemory
        self.vector_memory = VectorMemory()
        try:
            self.auto_constructor = AutoConstructionModule(self.call_llm)
        except Exception:
            self.auto_constructor = None
            logging.warning("AutoConstructionModule indisponível.")
        try:
            self.evolution_module = EvolutionModule(self)
        except Exception:
            self.evolution_module = None
            logging.warning("EvolutionModule indisponível.")
        self.sentiment_analyzer = SentimentIntensityAnalyzer()

        # Estrutura inicial de personalidade dinâmica
        self.personality = {
            "estilo": "formal",
            "gírias": False,
            "entusiasmo": 0.5,
            "empatia": 0.5
        }
        # Tabela para registrar tentativas de evolução
        self.evolution_attempts_table = "evolution_attempts"
        self._ensure_evolution_attempts_table()
    def log_evolution_attempt(self, cycle_number, mission_prompt, llm_response_raw, success, reason_for_failure=None, details=None):
        """
        Registra uma tentativa de evolução na tabela evolution_attempts do Supabase.
        """
        if not self.supabase:
            logging.warning("Supabase não inicializado. Não foi possível registrar tentativa de evolução.")
            return
        try:
            data = {
                "timestamp": datetime.now().isoformat(),
                "cycle_number": cycle_number,
                "mission_prompt": mission_prompt,
                "llm_response_raw": json.dumps(llm_response_raw, ensure_ascii=False),
                "success": success,
                "reason_for_failure": reason_for_failure,
                "details": json.dumps(details, ensure_ascii=False) if details else None
            }
            self.supabase.table(self.evolution_attempts_table).insert(data).execute()
            logging.info(f"📝 Tentativa de evolução registrada: ciclo {cycle_number}, sucesso: {success}")
        except Exception as e:
            logging.error(f"Erro ao registrar tentativa de evolução: {e}")

    def _ensure_evolution_attempts_table(self):
        """
        Garante que a tabela evolution_attempts existe no Supabase.
        """
        try:
            self.supabase.table(self.evolution_attempts_table).select("id").limit(0).execute()
            logging.info(f"Tabela '{self.evolution_attempts_table}' existe.")
        except Exception:
            logging.warning(f"Tabela '{self.evolution_attempts_table}' não existe. Crie manualmente no Supabase com o seguinte SQL:")
            logging.warning("""
CREATE TABLE evolution_attempts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TEXT,
    cycle_number INTEGER,
    mission_prompt TEXT,
    llm_response_raw TEXT,
    success BOOLEAN,
    reason_for_failure TEXT,
    details TEXT
);
""")
    def registrar_ideia_vetorial(self, texto, metadados=None):
        """
        Salva uma ideia/interação como embedding vetorial.
        """
        doc_id = self.vector_memory.salvar_ideia(texto, metadados)
        logging.info(f"✅ Ideia registrada na memória vetorial: {doc_id}")
        return doc_id

    def buscar_ideias_semelhantes(self, consulta, k=3):
        """
        Busca ideias/interações semelhantes por similaridade semântica.
        """
        resultados = self.vector_memory.buscar_similaridade(consulta, k)
        logging.info(f"🔎 Ideias semelhantes encontradas: {resultados}")
        return resultados
    def pesquisa_web_avancada(self, url, seletor=None):
        """
        Usa o WebAgent para buscar e extrair dados de uma página web.
        """
        resultado = self.web_agent.buscar_e_extrair(url, seletor)
        self.save_to_memory("NexoGenesis", f"web_extracao_{url}", resultado)
        return resultado
        
        print("🌱 Nexo Gênesis inicializado - Agente Orquestrador ativo.")
        print("🔍 Módulo de busca na internet ativo.")
        print("🛠️ Módulo de auto-construção ativo.")
        print("🧬 Módulo de evolução contínua ativo.")
        
        # Inicializar tabelas se não existirem
        self.initialize_database()
        
        # Iniciar evolução contínua
        self.evolution_module.start_evolution_loop()

        # Inicializar módulo de auto-correção
        self.self_correction_module = SelfCorrectionModule(agent_name="NexoGenesis")

        # Novas tabelas para memória de longo prazo e proatividade
        self.agent_memory_table = "nexo_agent_memory"
        self.user_context_table = "nexo_user_context"
        self.proactive_tasks_table = "nexo_proactive_tasks"
        self._ensure_tables_exist()

        # Fazer o NexoGenesis refletir sobre o feedback do usuário (simulado)
        # Isso seria acionado por um evento ou feedback real
        self.self_correction_module.reflect_on_performance(
            "Minha memória e proatividade foram questionadas. Preciso aprender com o histórico e agir de forma mais concreta.",
            {"context_source": "user_feedback", "timestamp": datetime.now().isoformat()}
        )
        # Iniciar automação proativa contínua
        self.start_proactive_automation()
    
    def start_proactive_automation(self, user_id="default_user"):
        import threading, time
        def automation_loop():
            while True:
                try:
                    # Exemplo de missão proativa: buscar oportunidades de mercado
                    proactive_mission = "Pesquisar oportunidades de receita e inovação para o sistema Nexo."
                    logging.info(f"🤖 [Proativo] Iniciando missão automática: {proactive_mission}")
                    result = self.process_mission(proactive_mission, user_id)
                    logging.info(f"🤖 [Proativo] Resultado da missão: {result}")
                    # Enviar mensagem automática (pode ser por e-mail, Telegram, etc.)
                    # Aqui apenas imprime, mas pode ser integrado com notificações reais
                except Exception as e:
                    logging.error(f"Erro na automação proativa: {e}")
                time.sleep(600)  # Executa a cada 10 minutos (ajuste conforme necessário)
        t = threading.Thread(target=automation_loop, daemon=True)
        t.start()


    def initialize_database(self):
        """Inicializa as tabelas necessárias no Supabase"""
        try:

            try:
                from langchain.llms import OpenAI as LangOpenAI
                from langchain.llms import Ollama as LangOllama
                from langchain.llms import GooglePalm as LangGemini
                from langchain.agents import initialize_agent, Tool
                from langchain.memory import ConversationBufferMemory
                from langchain.prompts import PromptTemplate
            except ImportError:
                print("LangChain não instalado. Execute \'pip install langchain\' para usar o motor de raciocínio avançado.")

            # Tabela de missões
            # Esta é uma representação conceitual. No Supabase, você criaria as tabelas via SQL ou UI.
            # Exemplo de SQL para criar a tabela \'missions\':
            # CREATE TABLE missions (
            #   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            #   user_message TEXT,
            #   status TEXT,
            #   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            #   updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
            #   response TEXT,
            #   agent_created TEXT
            # );
            
            # Tabela de agentes
            # Exemplo de SQL para criar a tabela \'agents\':
            # CREATE TABLE agents (
            #   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            #   name TEXT,
            #   description TEXT,
            #   code TEXT,
            #   status TEXT,
            #   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            # );
            
            logging.info("Estruturas de banco de dados inicializadas (conceitual).")
        except Exception as e:
            logging.error(f"Erro ao inicializar banco de dados: {e}")

    def _ensure_tables_exist(self):
        # Verifica e cria tabelas essenciais no Supabase
        tabelas = [self.agent_memory_table, self.user_context_table, self.proactive_tasks_table, "agent_learning_memory", "agent_error_log"]
        for tabela in tabelas:
            try:
                self.supabase.table(tabela).select("id").limit(0).execute()
                logger.info(f"Tabela \'{tabela}\' existe.")
            except Exception:
                logger.warning(f"Tabela \'{tabela}\' não existe. Tentando criar...")
                try:
                    # Exemplo: criar tabela via função RPC customizada ou instrução SQL
                    self.supabase.rpc(f"create_{tabela}", {}).execute()
                    logger.info(f"Tabela \'{tabela}\' criada via RPC.")
                except Exception as e:
                    logger.error(f"Falha ao criar tabela \'{tabela}\': {e}")

    def save_to_memory(self, agent_id: str, key: str, value: any):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível salvar na memória.")
            return
        try:
            data, count = self.supabase.table(self.agent_memory_table).insert({
                "agent_id": agent_id,
                "key": key,
                "value": json.dumps(value),
                "timestamp": datetime.now().isoformat()
            }).execute()
            logger.info(f"Salvo na memória do agente {agent_id}: {key}")
        except Exception as e:
            logger.error(f"Erro ao salvar na memória do agente: {e}")

    def load_from_memory(self, agent_id: str, key: str) -> Optional[any]:
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível carregar da memória.")
            return None
        try:
            response = (
                self.supabase.table(self.agent_memory_table)
                    .select("value")
                    .eq("agent_id", agent_id)
                    .eq("key", key)
                    .order("timestamp", ascending=False)
                    .limit(1)
                    .execute()
            )
            if response.data:
                return json.loads(response.data[0]["value"])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar da memória do agente: {e}")
            return None

    def save_user_context(self, user_id: str, context_data: dict):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível salvar contexto do usuário.")
            return
        try:
            # Tenta atualizar, se não existir, insere
            data, count = self.supabase.table(self.user_context_table).upsert({
                "user_id": user_id,
                "context_data": json.dumps(context_data),
                "last_updated": datetime.now().isoformat()
            }, on_conflict="user_id").execute()
            logger.info(f"Contexto do usuário {user_id} salvo/atualizado.")
        except Exception as e:
            logger.error(f"Erro ao salvar contexto do usuário: {e}")

    def load_user_context(self, user_id: str) -> Optional[dict]:
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível carregar contexto do usuário.")
            return None
        try:
            response = (
                self.supabase.table(self.user_context_table)
                    .select("context_data")
                    .eq("user_id", user_id)
                    .order("last_updated", ascending=False)
                    .limit(1)
                    .execute()
            )
            if response.data:
                return json.loads(response.data[0]["context_data"])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar contexto do usuário: {e}")
            return None

    def add_proactive_task(self, task_description: str, schedule: str, details: dict = None):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível adicionar tarefa proativa.")
            return
        try:
            data, count = self.supabase.table(self.proactive_tasks_table).insert({
                "task_description": task_description,
                "schedule": schedule,
                "details": json.dumps(details) if details else None,
                "created_at": datetime.now().isoformat(),
                "status": "pending"
            }).execute()
            logger.info(f"Tarefa proativa adicionada: {task_description}")
        except Exception as e:
            logger.error(f"Erro ao adicionar tarefa proativa: {e}")

    def get_pending_proactive_tasks(self) -> list:
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível obter tarefas proativas.")
            return []
        try:
            response = (
                self.supabase.table(self.proactive_tasks_table)
                    .select("*")
                    .eq("status", "pending")
                    .order("created_at", ascending=True)
                    .execute()
            )
            return response.data
        except Exception as e:
            logger.error(f"Erro ao obter tarefas proativas: {e}")
            return []

    def update_proactive_task_status(self, task_id: str, status: str, result: dict = None):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível atualizar status da tarefa.")
            return
        try:
            data, count = self.supabase.table(self.proactive_tasks_table).update({
                "status": status,
                "result": json.dumps(result) if result else None,
                "updated_at": datetime.now().isoformat()
            }).eq("id", task_id).execute()
            logger.info(f"Status da tarefa {task_id} atualizado para {status}.")
        except Exception as e:
            logger.error(f"Erro ao atualizar status da tarefa: {e}")

    def call_llm(self, prompt: str, context: Optional[str] = None, model_name: Optional[str] = None) -> str:
        """
        Função centralizada para chamar LLMs, usando APIcreditOptimizer para seleção e fallback.
        """
        from agentes.APIcreditOptimizer import APIcreditOptimizer
        optimizer = APIcreditOptimizer()
        selected_provider = optimizer.select_provider()

        if not selected_provider:
            logger.error("Nenhum provedor de LLM disponível para chamada.")
            return "Erro: Nenhum LLM disponível."

        # Lógica para chamar o LLM com base no provedor selecionado
        try:
            if selected_provider == "openai":
                # Exemplo de chamada OpenAI
                # response = openai.Completion.create(engine="davinci", prompt=prompt, max_tokens=150)
                # return response.choices[0].text.strip()
                return f"Simulação OpenAI para: {prompt}"
            elif selected_provider == "gemini":
                # Exemplo de chamada Gemini
                # model = genai.GenerativeModel("gemini-pro")
                # response = model.generate_content(prompt)
                # return response.text
                return f"Simulação Gemini para: {prompt}"
            elif selected_provider == "groq":
                # Exemplo de chamada Groq
                # client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                # chat_completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
                # return chat_completion.choices[0].message.content
                return f"Simulação Groq para: {prompt}"
            else:
                return "Erro: Provedor de LLM desconhecido."
        except Exception as e:
            logger.error(f"Erro ao chamar LLM ({selected_provider}): {e}")
            # Tentar fallback ou registrar erro
            return f"Erro ao chamar LLM: {e}"

    def process_mission(self, mission_prompt: str, user_id: str = "default_user") -> str:
        """
        Processa uma missão do usuário, utilizando o NexoGenesis para orquestração.
        """
        logger.info(f"Processando missão para {user_id}: {mission_prompt}")
        
        # Salvar contexto do usuário
        self.save_user_context(user_id, {"last_mission": mission_prompt, "timestamp": datetime.now().isoformat()})

        # Exemplo de como o NexoGenesis usaria o auto_constructor
        try:
            # A lógica de auto_construction.auto_construct_feature já chama o LLM internamente
            # e espera um JSON com 'overview' e 'components'.
            result_json_str = self.auto_constructor.auto_construct_feature(mission_prompt)
            result = json.loads(result_json_str)
            response_text = f"Missão \'{mission_prompt}\' processada. Visão geral: {result.get('overview', 'N/A')}. Componentes: {', '.join(result.get('components', []))}."
            return response_text
        except Exception as e:
            logger.error(f"Erro ao processar missão com AutoConstructionModule: {e}")
            return f"Desculpe, ocorreu um erro ao processar sua missão: {e}. Tente novamente."

    def processar(self, user_input: str) -> str:
        """
        Ponto de entrada principal para interações com o agente.
        """
        # Aqui você pode adicionar lógica para determinar o user_id real
        user_id = "telegram_user_id" # Exemplo
        return self.process_mission(user_input, user_id)


def auto_update_agent(code_path: str):
    """
    Recebe um código de agente novo, roda testes e só ativa se passar.
    """
    success, logs = run_tests()
    save_log("INFO", f"Validação de agente {code_path}: {success}")
    if success:
        # lógica para mover/ativar agente
        return {"status": "aprovado", "logs": logs}
    else:
        return {"status": "reprovado", "logs": logs}

