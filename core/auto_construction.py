class AutoConstructionModule:
    """
    Módulo de auto-construção do Nexo Gênesis
    Pipeline: Architect AI → Coder AI → Reviewer AI → Deployer AI
    """
    def __init__(self, llm_caller):
        self.supabase = get_supabase_client()
        self.search = InternetSearchModule()
        self.github = GitHubIntegration()
        self.llm_caller = llm_caller  # Referência para chamar LLMs
        self.construction_history = []

    def gerar_dockerfile(self, app_dir=".", python_version="3.12"):
        """
        Gera um Dockerfile básico para o projeto Python.
        """
        dockerfile = f"""
        FROM python:{python_version}-slim
        WORKDIR /app
        COPY {app_dir} /app
        RUN pip install --no-cache-dir -r requirements.txt
        CMD [\"python\", \"nexo.py\"]
        """
        with open("Dockerfile", "w") as f:
            f.write(dockerfile)
            logging.info("✅ Dockerfile gerado.")
        return dockerfile

    def gerar_script_deploy(self):
        """
        Gera um script de deploy simples (shell) para rodar o container Docker.
        """
        script = """
        #!/bin/bash
        docker build -t nexo-autonomo .
        docker run -d --name nexo-autonomo -p 5000:5000 nexo-autonomo
        """
        with open("deploy_nexo.sh", "w") as f:
            f.write(script)
            logging.info("✅ Script de deploy gerado.")
        return script
import os
import json
import subprocess
import logging
from typing import Any, Dict
from datetime import datetime
from dotenv import load_dotenv
from core.database import get_supabase_client
from core.internet_search import InternetSearchModule
from core.json_utils import (
    extract_json,
    safe_json_response,
    create_json_prompt,
    ARCHITECTURE_SCHEMA,
    CODE_IMPLEMENTATION_SCHEMA,
    REVIEW_SCHEMA,
    MISSION_INTERPRETATION_SCHEMA,
)
from core.github_integration import GitHubIntegration

load_dotenv()

class AutoConstructionModule:
    """
    Módulo de auto-construção do Nexo Gênesis
    Pipeline: Architect AI → Coder AI → Reviewer AI → Deployer AI
    """
    
    def __init__(self, llm_caller):
        self.supabase = get_supabase_client()
        self.search = InternetSearchModule()
        self.github = GitHubIntegration()
        self.llm_caller = llm_caller  # Referência para chamar LLMs
        self.construction_history = []

    def build_meta_prompt(self, context: str, objective: str) -> str:
        """
        Constrói o meta-prompt de auto-construção usando o template definido pelo usuário.
        Retorna o texto pronto para ser enviado ao LLM.
        """
        template = """
## Meta-Prompt de Auto-Construção para o NexoGênesis

Instrução: Assuma o papel de NexoGênesis, o Agente Orquestrador. Sua missão é executar um ciclo de Auto-Construção Avançada para aprimorar sua própria funcionalidade ou a de um agente subordinado, visando cumprir uma nova exigência do usuário ou corrigir uma falha de desempenho.

1. Análise da Missão e Contexto

Contexto Atual do Usuário/Sistema:
{context}

Objetivo de Auto-Construção:
{objective}

2. Plano de Ação Estruturado

Gere um plano de execução detalhado em formato JSON seguindo o esquema de interpretação de missões. O plano deve cobrir Diagnóstico, Geração de Código (arquivos a criar/modificar e o conteúdo), Testes (plano e/ou trechos de teste), Integração e Deploy.

3. Diretrizes de Execução

Ferramentas Disponíveis: InternetSearchModule, AutoConstructionModule, get_supabase_client().
Restrição de Saída: Responda APENAS com JSON válido seguindo o schema MISSION_INTERPRETATION_SCHEMA.

""".strip()

        return template.format(context=context, objective=objective)

    def auto_construct_from_meta(self, context: str, objective: str, allow_deploy: bool = False) -> Dict[str, Any]:
        """
        Wrapper que usa o meta-prompt para obter uma interpretação de missão do LLM.
        Se o LLM indicar `use_auto_construction: true` (ou equivalente), e `allow_deploy` for True,
        este método encaminhará para `auto_construct_feature` com o objetivo final.
        Retorna o JSON interpretado e, se aplicável, o resultado da construção automática.
        """
        try:
            logging.info("🔧 Construindo meta-prompt para auto-construção")
            prompt_text = self.build_meta_prompt(context, objective)

            # Envolver o prompt para forçar JSON conforme schema
            wrapped_prompt = create_json_prompt(prompt_text, MISSION_INTERPRETATION_SCHEMA)

            logging.info("📨 Chamando LLM para interpretar missão...")
            llm_response = self.llm_caller(wrapped_prompt, objective)

            interpreted = safe_json_response(llm_response, fallback_response={
                "action": "clarify",
                "agent_name": None,
                "description": "Falha na interpretação automática",
                "requirements": [],
                "response": llm_response[:500] if isinstance(llm_response, str) else str(llm_response),
                "use_auto_construction": False
            })

            result: Dict[str, Any] = {"interpreted_mission": interpreted}

            # Se o LLM indicar que devemos usar auto-construction e estamos autorizados
            if interpreted.get("use_auto_construction") and interpreted.get("action") in ("auto_construct", "create_agent"):
                if allow_deploy:
                    logging.info("🚀 Execução autorizada: iniciando auto_construct_feature")
                    construction_result = self.auto_construct_feature(objective)
                    result["construction_result"] = construction_result
                else:
                    logging.info("⚠️ Auto-construction requisitado mas 'allow_deploy' está False. Não executando.")
                    result["note"] = "Auto-construction requisitado pelo LLM, mas allow_deploy=False"

            return result
        except Exception as e:
            logging.exception("Erro em auto_construct_from_meta")
            return {"error": str(e)}
    
    def auto_construct_feature(self, feature_request):
        """
        Pipeline completo de auto-construção de uma nova funcionalidade
        """
        try:
            logging.info(f"🚀 Iniciando auto-construção: {feature_request}")

            # 0. Pesquisa de mercado proativa
            logging.info("🔎 Realizando pesquisa de mercado...")
            mercado_results = self.search.search_web(f"{feature_request} market analysis opportunities", 3)
            logging.info(f"Resultados da pesquisa de mercado: {json.dumps(mercado_results, indent=2)}")

            # 0.1 Análise e estudo proativo
            logging.info("📊 Analisando e estudando oportunidades...")
            estudo_prompt = f"Analise os resultados de mercado e gere oportunidades de receita e inovação para o sistema. Resultados: {json.dumps(mercado_results, indent=2)}"
            estudo_result = self.llm_caller(estudo_prompt, feature_request)
            logging.info(f"Estudo/Oportunidades: {estudo_result}")

            # 1. Architect AI - Planejamento
            architecture = self.architect_ai(feature_request)

            # 2. Coder AI - Implementação
            code = self.coder_ai(architecture)

            # 3. Reviewer AI - Revisão
            review = self.reviewer_ai(code, architecture)

            # Corrigir fluxo se review não vier no formato esperado
            if not isinstance(review, dict) or "approved" not in review:
                # Força formato esperado
                review_format = {
                    "approved": False,
                    "reason": "Review do LLM não retornou JSON válido ou sem chave 'approved'.",
                    "raw_review": review
                }
                return {
                    "success": False,
                    "feature": feature_request,
                    "error": "Review do LLM não retornou JSON válido ou sem chave 'approved'.",
                    "review": review_format,
                    "timestamp": datetime.now().isoformat()
                }

            # 4. Deployer AI - Deploy (se aprovado)
            if review["approved"]:
                deployment = self.deployer_ai(code, architecture)
                # 4.1 Gerar Dockerfile e script de deploy
                dockerfile = self.gerar_dockerfile()
                deploy_script = self.gerar_script_deploy()
                # 5. Commit automático no GitHub
                construction_result = {
                    "success": True,
                    "feature": feature_request,
                    "architecture": architecture,
                    "code": code,
                    "review": review,
                    "deployment": deployment,
                    "dockerfile": dockerfile,
                    "deploy_script": deploy_script,
                    "timestamp": datetime.now().isoformat()
                }
                if self.github.is_enabled():
                    logging.info("📡 Fazendo commit automático no GitHub...")
                    github_success = self.github.auto_commit_construction_result(construction_result)
                    construction_result["github_commit"] = github_success
                else:
                    logging.warning("⚠️ Integração GitHub desabilitada")
                    construction_result["github_commit"] = False
                return construction_result
            else:
                # Garante que sempre haja 'approved' e motivo
                return {
                    "success": False,
                    "feature": feature_request,
                    "approved": review.get("approved", False),
                    "reason": review.get("issues", ["Erro desconhecido"]),
                    "timestamp": datetime.now().isoformat()
                }

        except Exception as e:
            # Lógica para erro 403 e ação humana
            error_msg = str(e)
            if "403" in error_msg or "forbidden" in error_msg.lower():
                logging.error("Erro 403: API do Google. Necessária ação manual: ativar permissão no Google Cloud Console.")
                # Log especial para ação humana
                return {
                    "success": False,
                    "feature": feature_request,
                    "approved": False,
                    "error": error_msg,
                    "action_required": "Ativar permissão no Google Cloud Console.",
                    "timestamp": datetime.now().isoformat()
                }
            return {
                "success": False,
                "feature": feature_request,
                "error": error_msg,
                "timestamp": datetime.now().isoformat()
            }
    
    def architect_ai(self, feature_request):
        """
        Architect AI - Planeja a arquitetura da nova funcionalidade
        """
        logging.info("🏗️ Architect AI analisando requisitos...")

        # Busca informações relevantes na internet
        search_results = self.search.search_web(f"{feature_request} implementation architecture", 3)

        instruction = f"""
        Você é o Architect AI do ecossistema EcoGuardians.

        Requisito: {feature_request}

        Informações da internet:
        {json.dumps(search_results, indent=2)}

        Crie uma arquitetura detalhada seguindo os princípios éticos do EcoGuardians.
        """

        prompt = create_json_prompt(instruction, ARCHITECTURE_SCHEMA)

        response = self.llm_caller(prompt, feature_request)

        # Usar função robusta de extração JSON
        fallback = {
            "overview": f"Arquitetura para {feature_request}",
            "components": ["Componente principal"],
            "dependencies": [],
            "files_to_create": [],
            "files_to_modify": [],
            "database_changes": [],
            "api_endpoints": [],
            "testing_strategy": "Testes básicos",
            "deployment_steps": ["Deploy padrão"]
        }
        
        architecture = safe_json_response(response, fallback)
        self._log_construction_step("architect", feature_request, architecture)
        return architecture
    
    def coder_ai(self, architecture):
        """
        Coder AI - Implementa o código baseado na arquitetura
        """
        logging.info("💻 Coder AI implementando código...")

        # Busca exemplos de código relevantes
        tech_stack = " ".join(architecture.get("dependencies", []))
        code_examples = self.search.search_code_examples(tech_stack, architecture["overview"])

        instruction = f"""
        Você é o Coder AI do ecossistema EcoGuardians.

        Arquitetura:
        {json.dumps(architecture, indent=2)}

        Exemplos de código encontrados:
        {json.dumps(code_examples, indent=2)}

        Implemente o código completo seguindo a arquitetura.

        Garanta que o código:
        1. Siga os princípios éticos do EcoGuardians
        2. Seja bem documentado
        3. Inclua tratamento de erros
        4. Seja compatível com a estrutura existente
        """

        prompt = create_json_prompt(instruction, CODE_IMPLEMENTATION_SCHEMA)

        response = self.llm_caller(prompt, f"Implementar {architecture['overview']}")

        # Usar função robusta de extração JSON
        fallback = {
            "files": {},
            "installation_commands": [],
            "setup_instructions": []
        }

        code = safe_json_response(response, fallback)
        self._log_construction_step("coder", architecture["overview"], code)
        return code
    
    def reviewer_ai(self, code, architecture):
        """
        Reviewer AI - Revisa o código e arquitetura
        """
        logging.info("🔍 Reviewer AI analisando código...")

        instruction = f"""
        Você é o Reviewer AI do ecossistema EcoGuardians.

        Arquitetura:
        {json.dumps(architecture, indent=2)}

        Código implementado:
        {json.dumps(code, indent=2)}

        Faça uma revisão completa e retorne um JSON com as chaves:
        - approved (bool): se o código está pronto para deploy
        - score (int): nota de 0 a 10
        - strengths (list): pontos fortes
        - issues (list): problemas encontrados
        - suggestions (list): sugestões de melhoria
        - security_check (str): status de segurança
        - performance_check (str): status de performance
        - compatibility_check (str): status de compatibilidade
        Se não conseguir analisar, retorne approved=False e explique o motivo em issues.
        """

        prompt = create_json_prompt(instruction, REVIEW_SCHEMA)

        response = self.llm_caller(prompt, f"Revisar {architecture['overview']}")

        # Usar função robusta de extração JSON
        fallback = {
            "approved": False,
            "score": 0,
            "strengths": [],
            "issues": ["Erro na análise de revisão"],
            "suggestions": [],
            "security_check": "Falhou",
            "performance_check": "Falhou",
            "compatibility_check": "Falhou"
        }

        # Corrigir resposta se não vier JSON válido
        try:
            review = safe_json_response(response, fallback)
            if "approved" not in review:
                review["approved"] = False
                review["issues"] = review.get("issues", []) + ["Chave 'approved' ausente no retorno do LLM."]
        except Exception as e:
            review = fallback
            review["issues"].append(f"Erro ao extrair JSON: {e}")
        self._log_construction_step("reviewer", architecture["overview"], review)
        return review
    
    def deployer_ai(self, code, architecture):
        """
        Deployer AI - Faz o deploy do código aprovado
        """
        logging.info("🚀 Deployer AI fazendo deploy...")

        try:
            deployment_result = {
                "files_created": [],
                "files_modified": [],
                "commands_executed": [],
                "git_operations": [],
                "status": "success"
            }
            # 1. Criar/modificar arquivos
            # Se deploy automático estiver desabilitado, colocamos em staging
            allow_deploy = str(os.environ.get('AUTO_CONSTRUCTION_ALLOW_DEPLOY', '0')).lower() in ('1', 'true', 'yes')
            repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
            staged_id = None
            if not allow_deploy:
                # Criar pasta de staging com timestamp
                staged_id = f"build_{int(datetime.now().timestamp())}"
                staging_root = os.path.join(repo_root, 'autoconstruct_staging', staged_id)
                os.makedirs(staging_root, exist_ok=True)
                logging.info(f"🚧 Auto-construction em modo STAGING: {staging_root}")

            for file_path, content in code.get("files", {}).items():
                try:
                    if not allow_deploy:
                        # Salvar em staging mantendo a estrutura de diretórios
                        target = os.path.join(staging_root, file_path)
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        with open(target, 'w', encoding='utf-8') as f:
                            f.write(content)
                        deployment_result["files_created"].append(target)
                        logging.info(f"✅ Arquivo STAGED: {target}")
                    else:
                        # Deploy direto no repositório
                        target = os.path.join(repo_root, file_path)
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        with open(target, 'w', encoding='utf-8') as f:
                            f.write(content)
                        deployment_result["files_created"].append(target)
                        logging.info(f"✅ Arquivo criado: {target}")
                except Exception as e:
                    logging.error(f"❌ Erro ao criar {file_path}: {e}")
            
            # 2. Executar comandos de instalação (somente se permitido)
            if allow_deploy:
                for command in code.get("installation_commands", []):
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True)
                        deployment_result["commands_executed"].append({
                            "command": command,
                            "success": result.returncode == 0,
                            "output": result.stdout,
                            "error": result.stderr
                        })
                        logging.info(f"✅ Comando executado: {command}")
                    except Exception as e:
                        logging.error(f"❌ Erro ao executar {command}: {e}")
            else:
                deployment_result["staged"] = True
                deployment_result["staged_id"] = staged_id
                # salvar metadados de staging
                try:
                    meta = {
                        'staged_id': staged_id,
                        'feature': architecture.get('overview', 'unknown') if isinstance(globals().get('architecture', None), dict) else None,
                        'timestamp': datetime.now().isoformat(),
                        'files': list(code.get('files', {}).keys()),
                        'installation_commands': code.get('installation_commands', [])
                    }
                    meta_path = os.path.join(repo_root, 'autoconstruct_staging', staged_id, 'meta.json')
                    with open(meta_path, 'w', encoding='utf-8') as mf:
                        json.dump(meta, mf, ensure_ascii=False, indent=2)
                except Exception:
                    pass
            
            # 3. Operações Git (se em repositório)
            # 3. Operações Git (somente se permitido)
            try:
                if allow_deploy:
                    subprocess.run("git add .", shell=True, cwd=repo_root)
                    commit_message = f"Auto-construção: {architecture.get('overview', 'Nova funcionalidade')}"
                    subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd=repo_root)
                    deployment_result["git_operations"].append("commit")
                    logging.info("✅ Commit realizado")
                else:
                    logging.info("⚠️ Deploy automático desabilitado; build foi staged e não será commitado automaticamente.")
            except Exception as e:
                logging.warning(f"⚠️ Operações Git falharam: {e}")
            
            self._log_construction_step("deployer", architecture.get("overview", "unknown") if isinstance(architecture, dict) else str(architecture), deployment_result)
            return deployment_result
            
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "files_created": [],
                "files_modified": [],
                "commands_executed": [],
                "git_operations": []
            }
    
    def _log_construction_step(self, step, feature, result):
        """
        Registra cada etapa da construção
        """
        log_entry = {
            "step": step,
            "feature": feature,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        self.construction_history.append(log_entry)
        
        # Salvar no Supabase (conceitual)
        # self.supabase.table("construction_logs").insert(log_entry).execute()
    
    def get_construction_history(self):
        """
        Retorna histórico de construções
        """
        return self.construction_history

if __name__ == "__main__":
    # Teste do módulo
    logging.info("🧪 Testando módulo de auto-construção...")

    # Integração real com Gemini
    import google.generativeai as genai
    import os
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

    def llm_caller(prompt, context):
        try:
            model = genai.GenerativeModel('gemini-1.5-flash')
            response = model.generate_content(f"{prompt}\nContexto: {context}")
            return response.text
        except Exception as e:
            logging.error(f"Erro ao chamar Gemini: {e}")
            return '{"erro": "Falha na chamada Gemini"}'

    auto_constructor = AutoConstructionModule(llm_caller)
    result = auto_constructor.auto_construct_feature("Sistema de notificações por email")
    logging.info(f"Resultado: {result}")
