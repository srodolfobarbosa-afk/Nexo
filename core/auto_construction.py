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
            
            # 1. Architect AI - Planejamento
            architecture = self.architect_ai(feature_request)
            
            # 2. Coder AI - Implementação
            code = self.coder_ai(architecture)
            
            # 3. Reviewer AI - Revisão
            review = self.reviewer_ai(code, architecture)
            
            # 4. Deployer AI - Deploy (se aprovado)
            if review["approved"]:
                deployment = self.deployer_ai(code, architecture)
                
                # 5. Commit automático no GitHub
                construction_result = {
                    "success": True,
                    "feature": feature_request,
                    "architecture": architecture,
                    "code": code,
                    "review": review,
                    "deployment": deployment,
                    "timestamp": datetime.now().isoformat()
                }
                
                # Fazer commit automático no GitHub
                if self.github.is_enabled():
                    print("📡 Fazendo commit automático no GitHub...")
                    github_success = self.github.auto_commit_construction_result(construction_result)
                    construction_result["github_commit"] = github_success
                else:
                    print("⚠️ Integração GitHub desabilitada")
                    construction_result["github_commit"] = False
                
                return construction_result
            else:
                return {
                    "success": False,
                    "feature": feature_request,
                    "reason": review["issues"],
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "success": False,
                "feature": feature_request,
                "error": str(e),
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
        
        Faça uma revisão completa seguindo os critérios:
        1. Código segue princípios éticos do EcoGuardians
        2. Implementação está completa
        3. Não há vulnerabilidades de segurança
        4. Código é compatível com estrutura existente
        5. Score >= 7 para aprovação
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
        
        review = safe_json_response(response, fallback)
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
    
    # Simulação de LLM caller
    def mock_llm_caller(prompt, context):
        return '{"overview": "Teste", "components": ["teste"]}'
    
    auto_constructor = AutoConstructionModule(mock_llm_caller)
    result = auto_constructor.auto_construct_feature("Sistema de notificações por email")
    print(f"Resultado: {result}")
