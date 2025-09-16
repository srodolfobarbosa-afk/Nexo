import os
import base64
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class GitHubIntegration:
    """
    Módulo de integração GitHub para commits automáticos e controle de versão
    Permite ao Nexo Gênesis fazer commits automáticos das melhorias geradas
    """
    
    def __init__(self):
        self.github_token = os.environ.get("GITHUB_TOKEN")
        self.github_repo = os.environ.get("GITHUB_REPO", "srodolfobarbosa-afk/Nexo")
        self.base_url = f"https://api.github.com/repos/{self.github_repo}"
        self.headers = {
            "Authorization": f"token {self.github_token}",
            "Accept": "application/vnd.github.v3+json"
        }
        
        if not self.github_token:
            print("⚠️ GITHUB_TOKEN não encontrado. Funcionalidades GitHub desabilitadas.")
    
    def is_enabled(self):
        """Verifica se a integração GitHub está habilitada"""
        return bool(self.github_token)
    
    def get_file_content(self, file_path):
        """Obtém o conteúdo atual de um arquivo no repositório"""
        try:
            url = f"{self.base_url}/contents/{file_path}"
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                data = response.json()
                content = base64.b64decode(data["content"]).decode('utf-8')
                return {
                    "content": content,
                    "sha": data["sha"],
                    "exists": True
                }
            elif response.status_code == 404:
                return {
                    "content": "",
                    "sha": None,
                    "exists": False
                }
            else:
                raise Exception(f"Erro ao obter arquivo: {response.status_code} - {response.text}")
                
        except Exception as e:
            print(f"Erro ao obter conteúdo do arquivo {file_path}: {e}")
            return None
    
    def commit_file(self, file_path, content, message=None, branch="main"):
        """Faz commit de um arquivo no repositório"""
        if not self.is_enabled():
            print("⚠️ Integração GitHub desabilitada")
            return False
        
        try:
            # Obter informações do arquivo atual
            file_info = self.get_file_content(file_path)
            if not file_info:
                return False
            
            # Verificar se o conteúdo mudou
            if file_info["exists"] and file_info["content"] == content:
                print(f"📄 Arquivo {file_path} não modificado, pulando commit")
                return True
            
            # Preparar dados do commit
            if not message:
                action = "Atualizar" if file_info["exists"] else "Criar"
                message = f"🤖 {action} {file_path} - Auto-construção Nexo Gênesis"
            
            url = f"{self.base_url}/contents/{file_path}"
            data = {
                "message": message,
                "content": base64.b64encode(content.encode('utf-8')).decode('utf-8'),
                "branch": branch
            }
            
            # Incluir SHA se arquivo existe
            if file_info["sha"]:
                data["sha"] = file_info["sha"]
            
            response = requests.put(url, headers=self.headers, json=data)
            
            if response.status_code in [200, 201]:
                result = response.json()
                print(f"✅ Commit realizado: {file_path}")
                print(f"🔗 URL: {result['content']['html_url']}")
                return True
            else:
                print(f"❌ Erro no commit: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao fazer commit de {file_path}: {e}")
            return False
    
    def commit_multiple_files(self, files_dict, message=None, branch="main"):
        """Faz commit de múltiplos arquivos de uma vez"""
        if not self.is_enabled():
            print("⚠️ Integração GitHub desabilitada")
            return False
        
        try:
            # Obter SHA da branch
            branch_url = f"{self.base_url}/git/refs/heads/{branch}"
            branch_response = requests.get(branch_url, headers=self.headers)
            
            if branch_response.status_code != 200:
                print(f"❌ Erro ao obter branch {branch}")
                return False
            
            base_sha = branch_response.json()["object"]["sha"]
            
            # Criar tree com os arquivos
            tree_items = []
            for file_path, content in files_dict.items():
                # Criar blob para o arquivo
                blob_data = {
                    "content": content,
                    "encoding": "utf-8"
                }
                blob_response = requests.post(
                    f"{self.base_url}/git/blobs",
                    headers=self.headers,
                    json=blob_data
                )
                
                if blob_response.status_code == 201:
                    blob_sha = blob_response.json()["sha"]
                    tree_items.append({
                        "path": file_path,
                        "mode": "100644",
                        "type": "blob",
                        "sha": blob_sha
                    })
                else:
                    print(f"❌ Erro ao criar blob para {file_path}")
                    return False
            
            # Criar tree
            tree_data = {
                "base_tree": base_sha,
                "tree": tree_items
            }
            tree_response = requests.post(
                f"{self.base_url}/git/trees",
                headers=self.headers,
                json=tree_data
            )
            
            if tree_response.status_code != 201:
                print(f"❌ Erro ao criar tree")
                return False
            
            tree_sha = tree_response.json()["sha"]
            
            # Criar commit
            if not message:
                message = f"🤖 Auto-construção Nexo Gênesis - {len(files_dict)} arquivos atualizados"
            
            commit_data = {
                "message": message,
                "tree": tree_sha,
                "parents": [base_sha]
            }
            commit_response = requests.post(
                f"{self.base_url}/git/commits",
                headers=self.headers,
                json=commit_data
            )
            
            if commit_response.status_code != 201:
                print(f"❌ Erro ao criar commit")
                return False
            
            commit_sha = commit_response.json()["sha"]
            
            # Atualizar referência da branch
            ref_data = {
                "sha": commit_sha
            }
            ref_response = requests.patch(
                f"{self.base_url}/git/refs/heads/{branch}",
                headers=self.headers,
                json=ref_data
            )
            
            if ref_response.status_code == 200:
                print(f"✅ Commit múltiplo realizado: {len(files_dict)} arquivos")
                print(f"🔗 Commit SHA: {commit_sha}")
                return True
            else:
                print(f"❌ Erro ao atualizar branch")
                return False
                
        except Exception as e:
            print(f"❌ Erro no commit múltiplo: {e}")
            return False
    
    def create_pull_request(self, title, body, head_branch, base_branch="main"):
        """Cria um pull request"""
        if not self.is_enabled():
            return False
        
        try:
            data = {
                "title": title,
                "body": body,
                "head": head_branch,
                "base": base_branch
            }
            
            response = requests.post(
                f"{self.base_url}/pulls",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 201:
                pr_data = response.json()
                print(f"✅ Pull Request criado: {pr_data['html_url']}")
                return pr_data
            else:
                print(f"❌ Erro ao criar PR: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Erro ao criar pull request: {e}")
            return False
    
    def get_repository_info(self):
        """Obtém informações do repositório"""
        if not self.is_enabled():
            return None
        
        try:
            response = requests.get(self.base_url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"❌ Erro ao obter info do repo: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao obter informações do repositório: {e}")
            return None
    
    def trigger_deployment(self):
        """Dispara deployment via GitHub Actions (se configurado)"""
        if not self.is_enabled():
            return False
        
        try:
            # Dispara workflow de deployment
            data = {
                "event_type": "deploy",
                "client_payload": {
                    "triggered_by": "nexo_genesis",
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            response = requests.post(
                f"{self.base_url}/dispatches",
                headers=self.headers,
                json=data
            )
            
            if response.status_code == 204:
                print("✅ Deployment disparado via GitHub Actions")
                return True
            else:
                print(f"⚠️ Não foi possível disparar deployment: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ Erro ao disparar deployment: {e}")
            return False
    
    def auto_commit_construction_result(self, construction_result):
        """Faz commit automático dos resultados de auto-construção"""
        if not self.is_enabled() or not construction_result.get("success"):
            return False
        
        try:
            files_to_commit = construction_result.get("code", {}).get("files", {})
            
            if not files_to_commit:
                print("📄 Nenhum arquivo para commit")
                return True
            
            # Preparar mensagem de commit
            feature_name = construction_result.get("feature", "Nova funcionalidade")
            message = f"🚀 Auto-construção: {feature_name}\n\n"
            message += f"Arquivos criados/modificados: {len(files_to_commit)}\n"
            message += f"Timestamp: {construction_result.get('timestamp', 'N/A')}\n"
            message += f"Gerado por: Nexo Gênesis Auto-Construction"
            
            # Fazer commit múltiplo
            success = self.commit_multiple_files(files_to_commit, message)
            
            if success:
                # Tentar disparar deployment
                self.trigger_deployment()
            
            return success
            
        except Exception as e:
            print(f"❌ Erro no commit automático: {e}")
            return False

if __name__ == "__main__":
    # Teste do módulo
    github = GitHubIntegration()
    
    if github.is_enabled():
        print("🧪 Testando integração GitHub...")
        
        # Teste de informações do repositório
        repo_info = github.get_repository_info()
        if repo_info:
            print(f"📁 Repositório: {repo_info['full_name']}")
            print(f"🌟 Stars: {repo_info['stargazers_count']}")
        
        # Teste de commit simples
        test_content = f"# Teste de integração GitHub\n\nTimestamp: {datetime.now().isoformat()}"
        github.commit_file("test_github_integration.md", test_content, "🧪 Teste de integração GitHub")
        
    else:
        print("⚠️ Integração GitHub não configurada")
