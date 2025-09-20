from core.web_agent import WebAgent
import os
import json
import logging
from datetime import datetime
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
print(f"DEBUG: Chave da API do Gemini: {os.getenv('GOOGLE_API_KEY')}")

from typing import Optional
gemini_api_key = os.getenv('GEMINI_API_KEY')
try:
    if gemini_api_key:
        genai.configure(api_key=gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
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
            print(f"[AVISO] Pacotes faltando: {faltando}. Execute 'pip install -r requirements.txt'.")
        if env_faltando:
            print(f"[AVISO] Variáveis de ambiente faltando: {env_faltando}. Configure no .env ou render.yaml.")
        if not faltando and not env_faltando:
            print("[OK] Ambiente validado: todas dependências e variáveis presentes.")
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
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.search_module = InternetSearchModule() # Mantenha por enquanto
        self.web_agent = WebAgent() # Novo WebAgent
        print("🌐 Agente de navegação web (Playwright) ativo.")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.llm_provider = os.environ.get("NEXO_LLM_PROVIDER", "google")

        # Inicializar módulos de auto-construção, automação web e memória vetorial
        from core.vector_memory import VectorMemory
        self.vector_memory = VectorMemory()
        self.auto_constructor = AutoConstructionModule(self.call_llm)
        self.evolution_module = EvolutionModule(self)
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
            print("Supabase não inicializado. Não foi possível registrar tentativa de evolução.")
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
            print(f"📝 Tentativa de evolução registrada: ciclo {cycle_number}, sucesso: {success}")
        except Exception as e:
            print(f"Erro ao registrar tentativa de evolução: {e}")

    def _ensure_evolution_attempts_table(self):
        """
        Garante que a tabela evolution_attempts existe no Supabase.
        """
        try:
            self.supabase.table(self.evolution_attempts_table).select("id").limit(0).execute()
            print(f"Tabela '{self.evolution_attempts_table}' existe.")
        except Exception:
            print(f"Tabela '{self.evolution_attempts_table}' não existe. Crie manualmente no Supabase com o seguinte SQL:")
            print("""
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
        print(f"✅ Ideia registrada na memória vetorial: {doc_id}")
        return doc_id

    def buscar_ideias_semelhantes(self, consulta, k=3):
        """
        Busca ideias/interações semelhantes por similaridade semântica.
        """
        resultados = self.vector_memory.buscar_similaridade(consulta, k)
        print(f"🔎 Ideias semelhantes encontradas: {resultados}")
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
                    print(f"🤖 [Proativo] Iniciando missão automática: {proactive_mission}")
                    result = self.process_mission(proactive_mission, user_id)
                    print(f"🤖 [Proativo] Resultado da missão: {result}")
                    # Enviar mensagem automática (pode ser por e-mail, Telegram, etc.)
                    # Aqui apenas imprime, mas pode ser integrado com notificações reais
                except Exception as e:
                    print(f"Erro na automação proativa: {e}")
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
                print("LangChain não instalado. Execute 'pip install langchain' para usar o motor de raciocínio avançado.")

            # Tabela de missões
            # Esta é uma representação conceitual. No Supabase, você criaria as tabelas via SQL ou UI.
            # Exemplo de SQL para criar a tabela 'missions':
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
            # Exemplo de SQL para criar a tabela 'agents':
            # CREATE TABLE agents (
            #   id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
            #   name TEXT,
            #   description TEXT,
            #   code TEXT,
            #   status TEXT,
            #   created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
            # );
            
            print("Estruturas de banco de dados inicializadas (conceitual).")
        except Exception as e:
            print(f"Erro ao inicializar banco de dados: {e}")

    def _ensure_tables_exist(self):
        # Verifica e cria tabelas essenciais no Supabase
        tabelas = [self.agent_memory_table, self.user_context_table, self.proactive_tasks_table, "agent_learning_memory", "agent_error_log"]
        for tabela in tabelas:
            try:
                self.supabase.table(tabela).select("id").limit(0).execute()
                logger.info(f"Tabela '{tabela}' existe.")
            except Exception:
                logger.warning(f"Tabela '{tabela}' não existe. Tentando criar...")
                try:
                    # Exemplo: criar tabela via função RPC customizada ou instrução SQL
                    self.supabase.rpc(f"create_{tabela}", {}).execute()
                    logger.info(f"Tabela '{tabela}' criada via RPC.")
                except Exception as e:
                    logger.error(f"Falha ao criar tabela '{tabela}': {e}")

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
            # --- Integração LangChain ---
            self.langchain_enabled = False
            try:
                self.langchain_memory = ConversationBufferMemory(memory_key="chat_history", return_messages=True)
                self.langchain_tools = [
                    Tool(
                        name="BuscaWeb",
                        func=lambda q: str(self.search_module.search_web(q, 2)),
                        description="Busca informações na internet."
                    ),
                    Tool(
                        name="AutoConstrutor",
                        func=lambda f: str(self.auto_constructor.auto_construct_feature(f)),
                        description="Constrói funcionalidades automaticamente."
                    )
                ]
                self.langchain_llms = {}
                if self.openai_api_key:
                    self.langchain_llms["openai"] = LangOpenAI(openai_api_key=self.openai_api_key)
                if self.gemini_api_key:
                    self.langchain_llms["google"] = LangGemini(google_api_key=self.gemini_api_key)
                self.langchain_llms["ollama"] = LangOllama(model="llama2")
                self.langchain_enabled = True
            except Exception as e:
                print(f"Erro ao inicializar LangChain: {e}")
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
                .limit(1)
                .execute()
            )
            
            if response.data:
                return json.loads(response.data[0]["context_data"])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar contexto do usuário: {e}")
            return None

    def interpret_mission(self, user_message):
        """Interpreta uma missão em linguagem natural, agora com navegação web e reconhecimento de sentimento."""
        try:
            # Análise de sentimento
            sentiment = self.sentiment_analyzer.polarity_scores(user_message)
            sentiment_label = "neutro"
            if sentiment["compound"] >= 0.5:
                sentiment_label = "positivo"
            elif sentiment["compound"] <= -0.5:
                sentiment_label = "negativo"
            search_context = ""
            # Lógica para usar a navegação web em vez da busca simples
            if "pesquisar detalhadamente" in user_message.lower():
                import asyncio
                loop = asyncio.get_event_loop()
                search_results = loop.run_until_complete(self.web_agent.search_and_extract(user_message, 2))
                if search_results:
                    search_context = f"\n\nInformações detalhadas da internet:\n{json.dumps(search_results, indent=2)}"
            elif any(keyword in user_message.lower() for keyword in ["novo", "criar", "implementar", "desenvolver"]):
                search_results = self.search_module.search_web(f"{user_message} implementation best practices", 2)
                if search_results:
                    search_context = f"\n\nInformações relevantes da internet:\n{json.dumps(search_results, indent=2)}"
            instruction = f"""
            Você é o Nexo Gênesis, um agente orquestrador do ecossistema EcoGuardians.
            O sentimento do usuário é: {sentiment_label}
            Sua personalidade atual é: {json.dumps(self.personality, ensure_ascii=False)}
            Analise a seguinte missão do usuário e determine:
            1. Que tipo de agente ou funcionalidade é necessária
            2. Quais são os requisitos técnicos
            3. Se já existe um agente que pode fazer isso
            4. Qual seria o nome do novo agente (se necessário)
            5. Se deve usar auto-construção avançada para implementações complexas
            Missão: {user_message}{search_context}
            """
            prompt = create_json_prompt(instruction, MISSION_INTERPRETATION_SCHEMA)
            response = self.call_llm(prompt, user_message)
            # Usar função robusta de extração JSON
            fallback = {
                "action": "clarify",
                "agent_name": "Assistente",
                "description": "Agente de esclarecimento",
                "requirements": [],
                "response": f"Desculpe, houve um erro ao processar sua missão. Pode reformular?",
                "use_auto_construction": False
            }
            
            interpretation = safe_json_response(response, fallback)
            return interpretation
            
        except Exception as e:
            print(f"Erro ao interpretar missão: {e}")
            return {
                "action": "error",
                "response": f"Erro ao processar sua missão: {e}"
            }

    def choose_llm_model(self, user_message):
        """
        Escolhe o modelo LLM a ser usado com base na mensagem do usuário e na configuração.
        Prioriza LLMs pagos para tarefas críticas e LLMs de código aberto para rotinas ou fallback.
        """
        # Lógica de priorização e fallback
        if "urgente" in user_message.lower() or "estratégia" in user_message.lower():
            if self.openai_api_key: return "openai"
            if self.gemini_api_key: return "google"
            if self.groq_api_key: return "groq"
            return "ollama" # Fallback para Ollama se não houver chaves pagas
        elif "informação básica" in user_message.lower() or "rotina" in user_message.lower():
            return "ollama" # Prioriza Ollama para tarefas leves
        else:
            # Padrão: usa o provedor configurado, com fallback para outros pagos e depois Ollama
            if self.llm_provider == "google" and self.gemini_api_key: return "google"
            if self.llm_provider == "openai" and self.openai_api_key: return "openai"
            if self.llm_provider == "groq" and self.groq_api_key: return "groq"
            return "ollama" # Fallback final para Ollama

    def call_llm(self, prompt, user_message=""):
        """Chama o LLM configurado com lógica de fallback"""
        chosen_llm = self.choose_llm_model(user_message)
        
        try:
            if chosen_llm == "google":
                return self.call_gemini(prompt)
            elif chosen_llm == "openai":
                return self.call_openai(prompt)
            elif chosen_llm == "groq":
                return self.call_groq(prompt)
            elif chosen_llm == "ollama":
                return self.call_ollama(prompt)
            else:
                return '{"action": "error", "response": "Nenhum LLM configurado adequadamente ou disponível."}'
        except Exception as e:
            # Em caso de falha do LLM escolhido, tenta um fallback
            print(f"Erro ao chamar {chosen_llm}: {e}. Tentando fallback...")
            if chosen_llm != "ollama": # Se o erro não foi no Ollama, tenta Ollama como fallback
                try:
                    return self.call_ollama(prompt)
                except Exception as ollama_e:
                    return f'{{"action": "error", "response": "Erro ao chamar LLM e fallback: {e}, {ollama_e}"}}'
            return f'{{"action": "error", "response": "Erro ao chamar LLM: {e}"}}'

    def call_gemini(self, prompt):
        """Chama a API do Google Gemini"""
        if not self.gemini_api_key:
            raise ValueError("GEMINI_API_KEY não configurada.")
        import google.generativeai as genai
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text

    def call_openai(self, prompt):
        """Chama a API da OpenAI"""
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY não configurada.")
        url = "https://api.openai.com/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "gpt-3.5-turbo", # Pode ser configurado para gpt-4 ou outro
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erro na API OpenAI: {response.status_code} - {response.text}")

    def call_groq(self, prompt):
        """Chama a API do Groq"""
        if not self.groq_api_key:
            raise ValueError("GROQ_API_KEY não configurada.")
        url = "https://api.groq.com/openai/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.groq_api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "mixtral-8x7b-32768", # Modelo Groq, pode ser alterado
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000
        }
        
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            result = response.json()
            return result["choices"][0]["message"]["content"]
        else:
            raise Exception(f"Erro na API Groq: {response.status_code} - {response.text}")

    def call_ollama(self, prompt):
        """Chama a API do Ollama (assumindo que o servidor Ollama está rodando localmente ou acessível)"""
        try:
            # Para usar Ollama, você precisa ter o servidor Ollama rodando e um modelo puxado (ex: ollama pull llama2)
            # O modelo padrão aqui é 'llama2', mas pode ser configurado via variável de ambiente ou parâmetro.
            ollama_model = os.environ.get("OLLAMA_MODEL", "llama2")
            
            # A chamada ao Ollama é síncrona por padrão na biblioteca Python
            response = ollama.chat(model=ollama_model, messages=[{'role': 'user', 'content': prompt}])
            return response["message"]["content"]
        except Exception as e:
            raise Exception(f"Erro na API Ollama: {e}. Certifique-se de que o servidor Ollama está rodando e o modelo '{ollama_model}' está disponível.")

    def create_agent(self, agent_name, description, requirements):
        """Cria um novo agente baseado nas especificações"""
        try:
            # Gerar código do agente
            code_prompt = f"""
            Crie um agente Python chamado {agent_name} com as seguintes especificações:
            
            Descrição: {description}
            Requisitos: {requirements}
            
            O agente deve:
            1. Herdar a estrutura básica dos outros agentes (ex: EcoFinance.py)
            2. Conectar-se ao Supabase usando `core.database.get_supabase_client()`
            3. Ter métodos específicos para suas funcionalidades
            4. Incluir tratamento de erros
            5. Seguir os princípios éticos do EcoGuardians
            
            Retorne apenas o código Python completo, sem explicações adicionais ou blocos de markdown.
            """
            
            agent_code = self.call_llm(code_prompt, f"Gerar código para o agente {agent_name}")
            
            # Remover possíveis blocos de código markdown se o LLM retornar
            if agent_code.startswith("```python") and agent_code.endswith("```"):
                agent_code = agent_code[9:-3].strip()
            elif agent_code.startswith("```") and agent_code.endswith("```"):
                agent_code = agent_code[3:-3].strip()

            # Salvar no banco de dados (exemplo conceitual)
            # self.supabase.table("agents").insert({
            #     "name": agent_name,
            #     "description": description,
            #     "code": agent_code,
            #     "status": "created",
            #     "created_at": datetime.now().isoformat()
            # }).execute()
            
            # Salvar arquivo do agente
            agent_file_path = f"agentes/{agent_name}.py"
            with open(agent_file_path, 'w', encoding='utf-8') as f:
                f.write(agent_code)
            
            return {
                "success": True,
                "message": f"Agente {agent_name} criado com sucesso! Arquivo salvo em {agent_file_path}",
                "file_path": agent_file_path
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Erro ao criar agente: {e}"
            }

    def process_mission(self, user_message, user_id: str = "default_user"):
        """Processa uma missão completa do usuário, agora com memória de longo prazo e proatividade."""
        logger.info(f"NexoGenesis processando missão de {user_id}: {user_message}")
        # --- Orquestração CrewAI ---
        try:
            crew = self.iniciar_crewai()
            resultado = crew.kickoff()
            return f"[CrewAI] Resultado colaborativo: {resultado}"
        except Exception as e:
            print(f"Erro CrewAI: {e}")

        # Carregar contexto do usuário
        user_context = self.load_user_context(user_id) or {"history": []}
        user_context["history"].append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})

        try:
            # Salvar missão no banco (exemplo conceitual)
            # ...existing code...

            # Interpretar missão
            interpretation = self.interpret_mission(user_message)
            response_text = interpretation.get("response", "Processando sua missão...")

            # Lógica de auto-correção proativa
            erro_detectado = False
            if "erro" in response_text.lower() or "falha" in response_text.lower():
                erro_detectado = True
                self.self_correction_module.log_error(
                    error_type="Erro detectado na missão",
                    description=response_text,
                    context={"user_message": user_message, "timestamp": datetime.now().isoformat()}
                )
                self.self_correction_module.reflect_on_performance(
                    user_feedback=response_text,
                    current_context={"user_message": user_message, "timestamp": datetime.now().isoformat()}
                )
                # Acionar auto-construção para correção
                response_text += "\n\n🔧 Iniciando auto-correção proativa..."
                construction_result = self.auto_constructor.auto_construct_feature(f"Corrija: {user_message}")
                if construction_result["success"]:
                    response_text += f"\n✅ Auto-correção concluída!"
                else:
                    response_text += f"\n❌ Falha na auto-correção: {construction_result.get('reason', 'Erro desconhecido')}"

            # Fluxo normal de criação de agente ou auto-construção
            if interpretation.get("action") == "create_agent":
                agent_result = self.create_agent(
                    interpretation.get("agent_name"),
                    interpretation.get("description"),
                    interpretation.get("requirements")
                )
                if agent_result["success"]:
                    response_text += "\n\n✅ " + agent_result.get("message", "")
                else:
                    response_text += "\n\n❌ " + agent_result.get("message", "Erro desconhecido")

            elif interpretation.get("action") == "auto_construct" or interpretation.get("use_auto_construction"):
                response_text += "\n\n🛠️ Iniciando auto-construção avançada..."
                construction_result = self.auto_constructor.auto_construct_feature(user_message)
                if construction_result["success"]:
                    response_text += f"\n\n✅ Auto-construção concluída com sucesso!"
                    response_text += f"\n📁 Arquivos criados: {len(construction_result.get('code', {}).get('files', {}))}"
                    response_text += f"\n🔧 Deploy realizado: {construction_result.get('deployment', {}).get('status', 'N/A')}"
                else:
                    response_text += f"\n\n❌ Auto-construção falhou: {construction_result.get('reason', 'Erro desconhecido')}"

            # Salvar contexto atualizado
            user_context["history"].append({"role": "nexo", "content": response_text, "timestamp": datetime.now().isoformat()})
            self.save_user_context(user_id, user_context)

            # Verificar proatividade após processar a mensagem
            self.check_for_proactive_tasks(user_id, user_message, response_text)

            # Atualizar personalidade com base na mensagem do usuário
            self.update_personality(user_message)

            return response_text

        except Exception as e:
            logger.error(f"Erro ao processar missão: {e}")
            return f"Erro ao processar missão: {e}"

    def update_personality(self, user_message):
        """Evolui a personalidade do Nexo conforme o estilo do usuário."""
        # Detecta gírias e tom descontraído
        gírias = ["mano", "véi", "top", "massa", "bora", "tipo assim", "sussa", "de boa"]
        if any(g in user_message.lower() for g in gírias):
            self.personality["gírias"] = True
            self.personality["estilo"] = "descontraído"
            self.personality["entusiasmo"] = min(1.0, self.personality["entusiasmo"] + 0.1)
        # Detecta entusiasmo
        if any(e in user_message.lower() for e in ["!", "incrível", "sensacional", "show"]):
            self.personality["entusiasmo"] = min(1.0, self.personality["entusiasmo"] + 0.2)
        # Detecta frustração
        if any(f in user_message.lower() for f in ["droga", "aff", "poxa", "chato", "frustrado"]):
            self.personality["empatia"] = min(1.0, self.personality["empatia"] + 0.2)
            self.personality["estilo"] = "empático"
        # ...pode evoluir com mais regras...

    def get_status(self):
        """Retorna o status atual do ecossistema"""
        # Status dos módulos de auto-construção
        evolution_status = self.evolution_module.get_evolution_status()
        status = {
            "nexo_genesis": "ativo",
            "agentes_criados": 1,  # EcoFinance (inicialmente)
            "missoes_processadas": 0,
            "ultima_atividade": datetime.now().isoformat(),
            "modules": {
                "search": "ativo",
                "auto_construction": "ativo",
                "evolution": "ativo" if evolution_status["is_evolving"] else "inativo"
            },
            "evolution": evolution_status,
            "capabilities": [
                "Interpretação de missões em linguagem natural",
                "Geração de código de agente",
                "Auto-construção avançada de funcionalidades",
                "Otimização de uso de LLM (custo/qualidade)",
                "Memória de longo prazo via Supabase",
                "Mecanismo de proatividade"
            ]
        }
        return status

    def schedule_proactive_task(self, user_id: str, description: str, task_type: str):
        if not self.supabase:
            logger.warning("Supabase não inicializado. Não foi possível agendar tarefa proativa.")
            return
        try:
            data, count = self.supabase.table(self.proactive_tasks_table).insert({
                "user_id": user_id,
                "description": description,
                "task_type": task_type,
                "status": "pending",
                "scheduled_at": datetime.now().isoformat()
            }).execute()
            logger.info(f"Tarefa proativa agendada no Supabase para {user_id}: {description}")
        except Exception as e:
            logger.error(f"Erro ao agendar tarefa proativa: {e}")

    def monitor_logs_and_alert(self):
        """Analisa os logs, identifica erros recorrentes e envia alertas autônomos."""
        import os
        import smtplib
        from email.mime.text import MIMEText
        log_path = 'logs/evolution_20250919.json'  # Exemplo de log do dia
        if not os.path.exists(log_path):
            return
        with open(log_path, 'r', encoding='utf-8') as f:
            log_data = f.read()
        # Detecta erro crítico
        if 'CRITICAL' in log_data or 'Traceback' in log_data:
            # Registrar na memória para auto-correção
            self.self_correction_module.log_error(
                error_type="Erro crítico detectado no log",
                description=log_data[-1000:],
                context={"timestamp": datetime.now().isoformat()}
            )
            # Enviar alerta por e-mail (exemplo)
            try:
                msg = MIMEText(f"Erro crítico detectado no Nexo:\n{log_data[-1000:]}")
                msg['Subject'] = 'Alerta Crítico Nexo'
                msg['From'] = 'nexo@autonomo.com'
                msg['To'] = self.owner_info['email']
                s = smtplib.SMTP('localhost')
                s.send_message(msg)
                s.quit()
            except Exception as e:
                print(f"Falha ao enviar alerta por e-mail: {e}")
            # Enviar alerta por Telegram (exemplo)
            try:
                chat_id = self.owner_info['chat_id_telegram']
                token = os.getenv('TELEGRAM_BOT_TOKEN')
                if token:
                    import requests
                    url = f"https://api.telegram.org/bot{token}/sendMessage"
                    payload = {"chat_id": chat_id, "text": f"[Nexo] Erro crítico detectado!"}
                    requests.post(url, data=payload)
            except Exception as e:
                print(f"Falha ao enviar alerta por Telegram: {e}")

    def monitor_resources_and_adapt(self):
        """Monitora CPU/memória e adapta o comportamento do Nexo para evitar falhas."""
        import psutil
        cpu = psutil.cpu_percent(interval=1)
        mem = psutil.virtual_memory().percent
        # Se sobrecarregado, adapta o comportamento
        if cpu > 85 or mem > 85:
            self.self_correction_module.log_error(
                error_type="Sobrecarga detectada",
                description=f"CPU: {cpu}%, Memória: {mem}%",
                context={"timestamp": datetime.now().isoformat()}
            )
            # Limitar missões simultâneas (exemplo)
            self.max_parallel_missions = 1
            # Trocar para LLM mais leve
            self.llm_mode = "ollama"
            print(f"⚠️ Nexo adaptou para modo leve: CPU={cpu}%, Mem={mem}%")
        else:
            self.max_parallel_missions = 5
            self.llm_mode = "default"

    def automatic_backup(self):
        """Realiza backup automático do banco Supabase e dos arquivos de código gerados."""
        import shutil
        import os
        # Backup dos arquivos de código
        backup_dir = f"backups/backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        os.makedirs(backup_dir, exist_ok=True)
        for pasta in ["core", "agentes", "src"]:
            if os.path.exists(pasta):
                shutil.copytree(pasta, f"{backup_dir}/{pasta}")
        # Backup do banco Supabase (exemplo: exporta dados para JSON)
        try:
            if self.supabase:
                tables = ["nexo_agents", "nexo_missions", "nexo_proactive_tasks"]
                for table in tables:
                    data = self.supabase.table(table).select("*").execute().data
                    with open(f"{backup_dir}/{table}.json", "w", encoding="utf-8") as f:
                        import json
                        json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Falha no backup do Supabase: {e}")
        print(f"🗄️ Backup automático realizado em {backup_dir}")

    def log_evolution_attempt(self, cycle_number, mission_prompt, llm_response_raw, success, reason_for_failure, details):
        """Registra uma tentativa de evolução na tabela evolution_attempts do Supabase."""
        import uuid
        try:
            if self.supabase:
                self.supabase.table("evolution_attempts").insert({
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "cycle_number": cycle_number,
                    "mission_prompt": mission_prompt,
                    "llm_response_raw": llm_response_raw,
                    "success": success,
                    "reason_for_failure": reason_for_failure,
                    "details": json.dumps(details, ensure_ascii=False)
                }).execute()
                print(f"🧬 Tentativa de evolução registrada no Supabase: ciclo {cycle_number}")
        except Exception as e:
            print(f"Erro ao registrar tentativa de evolução: {e}")

# Exemplo de uso (para testes locais)
if __name__ == "__main__":
    NexoGenesisAgent.validar_ambiente()
    # Certifique-se de que SUPABASE_URL e SUPABASE_KEY estão no seu .env
    # e que as tabelas existem ou serão criadas automaticamente pelo Supabase
    nexo_genesis = NexoGenesisAgent() # Alterado para NexoGenesisAgent
    
    test_user_id = "test_user_123"
    
    print("\n--- Teste de Mensagem 1 ---")
    response1 = nexo_genesis.process_mission("Olá Nexo, como você está?", test_user_id)
    print(f"Resposta do Nexo: {response1}")
    
    print("\n--- Teste de Mensagem 2 ---")
    response2 = nexo_genesis.process_mission("Preciso de ajuda com um problema de deployment no Render.", test_user_id)
    print(f"Resposta do Nexo: {response2}")
    
    print("\n--- Teste de Mensagem 3 ---")
    response3 = nexo_genesis.process_mission("Qual o status da minha memória?", test_user_id)
    print(f"Resposta do Nexo: {response3}")
    
    print("\n--- Teste de Mensagem 4 ---")
    response4 = nexo_genesis.process_mission("Quero otimizar meus créditos de API.", test_user_id)
    print(f"Resposta do Nexo: {response4}")
    
    print("\n--- Teste de Mensagem 5 ---")
    response5 = nexo_genesis.process_mission("Você é proativo?", test_user_id)
    print(f"Resposta do Nexo: {response5}")

    print("\n--- Verificando memória do agente ---")
    nexo_genesis.save_to_memory("NexoGenesis", "last_thought", "Refletindo sobre proatividade.")
    last_thought = nexo_genesis.load_from_memory("NexoGenesis", "last_thought")
    print(f"Último pensamento do NexoGenesis: {last_thought}")

    print("\n--- Verificando contexto do usuário ---")
    user_ctx = nexo_genesis.load_user_context(test_user_id)
    print(f"Contexto do usuário {test_user_id}: {user_ctx}")

    print("\n--- Verificando tarefas proativas agendadas (simulado) ---")
    # Em um sistema real, haveria uma forma de consultar a tabela proactive_tasks_table
    print("Verifique a tabela 'nexo_proactive_tasks' no Supabase para ver as tarefas agendadas.")

