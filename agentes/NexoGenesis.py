import os
import json
import logging
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

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

load_dotenv()

# Configuração de logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class NexoGenesisAgent:
    def __init__(self):
        # Manter a inicialização original do Supabase via get_supabase_client()
        self.supabase = get_supabase_client()
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
        self.openai_api_key = os.environ.get("OPENAI_API_KEY")
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.llm_provider = os.environ.get("NEXO_LLM_PROVIDER", "google")
        
        # Inicializar módulos de auto-construção
        self.search_module = InternetSearchModule()
        self.auto_constructor = AutoConstructionModule(self.call_llm)
        self.evolution_module = EvolutionModule(self)
        
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


    def initialize_database(self):
        """Inicializa as tabelas necessárias no Supabase"""
        try:
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
        # Esta é uma simulação. Em um ambiente real, você usaria migrações ou um ORM.
        # Para este contexto, vamos apenas logar que as tabelas seriam verificadas/criadas.
        logger.info(f"Verificando/Criando tabela: {self.agent_memory_table}")
        logger.info(f"Verificando/Criando tabela: {self.user_context_table}")
        logger.info(f"Verificando/Criando tabela: {self.proactive_tasks_table}")
        # Exemplo de como criar uma tabela se não existir (requer permissões de DDL)
        # try:
        #     self.supabase.table(self.agent_memory_table).select("id").limit(0).execute()
        # except Exception:
        #     self.supabase.rpc("create_agent_memory_table", {}).execute()

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
            response = self.supabase.table(self.agent_memory_table)
            .select("value")
            .eq("agent_id", agent_id)
            .eq("key", key)
            .order("timestamp", ascending=False)
            .limit(1)
            .execute()
            
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
            response = self.supabase.table(self.user_context_table)
            .select("context_data")
            .eq("user_id", user_id)
            .limit(1)
            .execute()
            
            if response.data:
                return json.loads(response.data[0]["context_data"])
            return None
        except Exception as e:
            logger.error(f"Erro ao carregar contexto do usuário: {e}")
            return None

    def interpret_mission(self, user_message):
        """Interpreta uma missão em linguagem natural"""
        try:
            # Buscar informações relevantes na internet se necessário
            search_context = ""
            if any(keyword in user_message.lower() for keyword in ["novo", "criar", "implementar", "desenvolver"]):
                search_results = self.search_module.search_web(f"{user_message} implementation best practices", 2)
                if search_results:
                    search_context = f"\n\nInformações relevantes da internet:\n{json.dumps(search_results, indent=2)}"
            
            instruction = f"""
            Você é o Nexo Gênesis, um agente orquestrador do ecossistema EcoGuardians.
            
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
        
        # Carregar contexto do usuário
        user_context = self.load_user_context(user_id) or {"history": []}
        user_context["history"].append({"role": "user", "content": user_message, "timestamp": datetime.now().isoformat()})

        try:
            # Salvar missão no banco (exemplo conceitual)
            # mission_data = {
            #     "user_message": user_message,
            #     "status": "processing",
            #     "created_at": datetime.now().isoformat()
            # }
            # self.supabase.table("missions").insert(mission_data).execute()
            
            # Interpretar missão
            interpretation = self.interpret_mission(user_message)
            
            response_text = interpretation.get("response", "Processando sua missão...")
            
            if interpretation.get("action") == "create_agent":
                # Criar novo agente
                agent_result = self.create_agent(
                    interpretation.get("agent_name"),
                    interpretation.get("description"),
                    interpretation.get("requirements")
                )
                
                if agent_result["success"]:
                    response_text += "\n\n✅ " + agent_result.get("message", "")
                    # mission_data["agent_created"] = interpretation.get("agent_name")
                else:
                    response_text += "\n\n❌ " + agent_result.get("message", "Erro desconhecido")
            
            elif interpretation.get("action") == "auto_construct" or interpretation.get("use_auto_construction"):
                # Usar auto-construção avançada
                response_text += "\n\n🛠️ Iniciando auto-construção avançada..."
                
                construction_result = self.auto_constructor.auto_construct_feature(user_message)
                
                if construction_result["success"]:
                    response_text += f"\n\n✅ Auto-construção concluída com sucesso!"
                    response_text += f"\n📁 Arquivos criados: {len(construction_result.get('code', {}).get('files', {}))}"
                    response_text += f"\n🔧 Deploy realizado: {construction_result.get('deployment', {}).get('status', 'N/A')}"
                else:
                    response_text += f"\n\n❌ Auto-construção falhou: {construction_result.get('reason', 'Erro desconhecido')}"
                
            # mission_data["response"] = response_text
            # mission_data["status"] = "completed"
            # mission_data["updated_at"] = datetime.now().isoformat()
            # self.supabase.table("missions").update(mission_data).eq("id", mission_data["id"]).execute()
            
            # Salvar contexto atualizado
            user_context["history"].append({"role": "nexo", "content": response_text, "timestamp": datetime.now().isoformat()})
            self.save_user_context(user_id, user_context)
            
            # Verificar proatividade após processar a mensagem
            self.check_for_proactive_tasks(user_id, user_message, response_text)

            return response_text
            
        except Exception as e:
            logger.error(f"Erro ao processar missão: {e}")
            return f"Erro ao processar missão: {e}"

    def get_status(self):
        """Retorna o status atual do ecossistema"""
        try:
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
        except Exception as e:
            logger.error(f"Erro ao obter status do NexoGenesis: {e}")
            return {"nexo_genesis": "erro", "details": str(e)}

    def check_for_proactive_tasks(self, user_id: str, last_user_message: str, last_nexo_response: str):
        """Verifica se há oportunidades para ações proativas com base no contexto."""
        logger.info(f"Verificando tarefas proativas para o usuário {user_id}...")
        
        # Exemplo de lógica proativa (pode ser expandida com modelos de IA)
        if "problema de deployment" in last_user_message.lower() or "render" in last_user_message.lower():
            task_description = "Monitorar o status do deployment no Render e notificar o usuário sobre quaisquer mudanças ou erros."
            self.schedule_proactive_task(user_id, task_description, "deployment_monitoring")
            logger.info(f"Tarefa proativa agendada: {task_description}")
            
        elif "otimizar créditos" in last_user_message.lower() or "créditos" in last_user_message.lower():
            task_description = "Analisar o uso de créditos da API e sugerir otimizações."
            self.schedule_proactive_task(user_id, task_description, "credit_optimization")
            logger.info(f"Tarefa proativa agendada: {task_description}")

        # Outras lógicas proativas podem ser adicionadas aqui

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

# Exemplo de uso (para testes locais)
if __name__ == "__main__":
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

