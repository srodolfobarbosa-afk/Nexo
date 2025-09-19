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
        print("✅ Dockerfile gerado.")
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
        print("✅ Script de deploy gerado.")
        return script
import os
import json
import subprocess
from datetime import datetime
from dotenv import load_dotenv
from core.database import get_supabase_client
from core.internet_search import InternetSearchModule
from core.json_utils import extract_json, safe_json_response, create_json_prompt, ARCHITECTURE_SCHEMA, CODE_IMPLEMENTATION_SCHEMA, REVIEW_SCHEMA
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
    
    def auto_construct_feature(self, feature_request):
        """
        Pipeline completo de auto-construção de uma nova funcionalidade
        """
        try:
            print(f"🚀 Iniciando auto-construção: {feature_request}")

            # 0. Pesquisa de mercado proativa
            print("🔎 Realizando pesquisa de mercado...")
            mercado_results = self.search.search_web(f"{feature_request} market analysis opportunities", 3)
            print(f"Resultados da pesquisa de mercado: {json.dumps(mercado_results, indent=2)}")

            # 0.1 Análise e estudo proativo
            print("📊 Analisando e estudando oportunidades...")
            estudo_prompt = f"Analise os resultados de mercado e gere oportunidades de receita e inovação para o sistema. Resultados: {json.dumps(mercado_results, indent=2)}"
            estudo_result = self.llm_caller(estudo_prompt, feature_request)
            print(f"Estudo/Oportunidades: {estudo_result}")

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
                    print("📡 Fazendo commit automático no GitHub...")
                    github_success = self.github.auto_commit_construction_result(construction_result)
                    construction_result["github_commit"] = github_success
                else:
                    print("⚠️ Integração GitHub desabilitada")
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
                print("Erro 403: API do Google. Necessária ação manual: ativar permissão no Google Cloud Console.")
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
        print("🏗️ Architect AI analisando requisitos...")
        
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
        print("💻 Coder AI implementando código...")
        
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
        print("🔍 Reviewer AI analisando código...")
        
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
        print("🚀 Deployer AI fazendo deploy...")
        
        try:
            deployment_result = {
                "files_created": [],
                "files_modified": [],
                "commands_executed": [],
                "git_operations": [],
                "status": "success"
            }
            
            # 1. Criar/modificar arquivos
            for file_path, content in code.get("files", {}).items():
                try:
                    # Garantir que o diretório existe
                    os.makedirs(os.path.dirname(file_path), exist_ok=True)
                    
                    # Escrever arquivo
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                    
                    deployment_result["files_created"].append(file_path)
                    print(f"✅ Arquivo criado: {file_path}")
                    
                except Exception as e:
                    print(f"❌ Erro ao criar {file_path}: {e}")
            
            # 2. Executar comandos de instalação
            for command in code.get("installation_commands", []):
                try:
                    result = subprocess.run(command, shell=True, capture_output=True, text=True)
                    deployment_result["commands_executed"].append({
                        "command": command,
                        "success": result.returncode == 0,
                        "output": result.stdout,
                        "error": result.stderr
                    })
                    print(f"✅ Comando executado: {command}")
                    
                except Exception as e:
                    print(f"❌ Erro ao executar {command}: {e}")
            
            # 3. Operações Git (se em repositório)
            try:
                # Add arquivos ao git
                subprocess.run("git add .", shell=True, cwd="/home/ubuntu/Nexo")
                
                # Commit
                commit_message = f"Auto-construção: {architecture.get('overview', 'Nova funcionalidade')}"
                subprocess.run(f'git commit -m "{commit_message}"', shell=True, cwd="/home/ubuntu/Nexo")
                
                deployment_result["git_operations"].append("commit")
                print("✅ Commit realizado")
                
            except Exception as e:
                print(f"⚠️ Operações Git falharam: {e}")
            
            self._log_construction_step("deployer", architecture["overview"], deployment_result)
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
    print("🧪 Testando módulo de auto-construção...")
    
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
            print(f"Erro ao chamar Gemini: {e}")
            return '{"erro": "Falha na chamada Gemini"}'

    auto_constructor = AutoConstructionModule(llm_caller)
    result = auto_constructor.auto_construct_feature("Sistema de notificações por email")
    print(f"Resultado: {result}")
