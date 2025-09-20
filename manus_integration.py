"""
Integração com API do Manus para comunicação tripartite
"""

import os
import json
import logging
import requests
from datetime import datetime
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

# Configurações
MANUS_API_URL = os.environ.get('MANUS_API_URL', 'https://api.manus.im')
MANUS_API_KEY = os.environ.get('MANUS_API_KEY', '')

logger = logging.getLogger(__name__)

class ManusIntegration:
    def __init__(self):
        self.api_url = MANUS_API_URL
        self.api_key = MANUS_API_KEY
        self.api_available = False  # API ainda não está publicamente disponível
        
        if not self.api_key:
            logger.info("API do Manus ainda não está publicamente disponível. Aguardando lançamento oficial.")
        else:
            self.session = requests.Session()
            # Configurar headers padrão
            self.session.headers.update({
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            })
            self.api_available = True
    
    def create_task(self, message: str, context: List[Dict] = None) -> Dict:
        """Criar uma tarefa no Manus para processar a mensagem"""
        if not self.api_available:
            logger.info("API do Manus ainda não está publicamente disponível. Aguardando lançamento oficial.")
            return {
                "status": "pending_api_launch",
                "message": "Integração com Manus será ativada quando a API oficial for lançada publicamente.",
                "api_status": "Aguardando lançamento - Currently in private beta",
                "expected_phases": [
                    "Phase 2: Early Access (Coming soon)",
                    "Phase 3: Public Release (Full access)"
                ],
                "timestamp": datetime.now().isoformat()
            }
        
        try:
            # Preparar payload para criação de tarefa
            task_data = {
                "goal": f"Processar mensagem do usuário: {message}",
                "context": {
                    "user_message": message,
                    "conversation_history": context or [],
                    "source": "nexo_integration",
                    "timestamp": datetime.now().isoformat()
                },
                "priority": "normal",
                "auto_execute": True
            }
            
            # Implementar chamada real para a API do Manus
            response = self.session.post(f"{self.api_url}/tasks", json=task_data)
            response.raise_for_status()  # Lança um erro para status 4xx ou 5xx
            
            # Retorna o JSON da resposta da API
            return response.json()
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição para a API Manus: {e}")
            return {
                "error": f"Erro de comunicação com a API: {str(e)}",
                "status": "failed"
            }
    
    def get_task_status(self, task_id: str) -> Dict:
        """Verificar status de uma tarefa"""
        if not self.api_available:
            return {
                "task_id": task_id,
                "status": "pending_api_launch",
                "message": "API do Manus ainda não está disponível publicamente"
            }
            
        try:
            # Implementar chamada real para verificar o status
            response = self.session.get(f"{self.api_url}/tasks/{task_id}")
            response.raise_for_status()
            
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao verificar status da tarefa: {e}")
            return {"error": str(e)}
    
    def list_capabilities(self) -> Dict:
        """Listar capacidades disponíveis do Manus"""
        return {
            "analysis": {
                "description": "Análise de dados e informações",
                "capabilities": [
                    "Pesquisa em múltiplas fontes",
                    "Análise de tendências",
                    "Síntese de informações",
                    "Geração de insights"
                ]
            },
            "creation": {
                "description": "Criação de conteúdo e soluções",
                "capabilities": [
                    "Documentos técnicos",
                    "Códigos e aplicações",
                    "Estratégias de negócio",
                    "Materiais educativos"
                ]
            },
            "automation": {
                "description": "Automação de processos",
                "capabilities": [
                    "Workflows automatizados",
                    "Integração de sistemas",
                    "Coleta de dados",
                    "Geração de relatórios"
                ]
            },
            "integration": {
                "description": "Integração com sistemas externos",
                "capabilities": [
                    "APIs REST/GraphQL",
                    "Webhooks",
                    "Bancos de dados",
                    "Serviços em nuvem"
                ]
            }
        }

# Instância global
# Esta instância só será criada se a chave da API for válida
try:
    manus_integration = ManusIntegration()
except ValueError:
    manus_integration = None # Define como None se a chave não existir

def call_manus_api(message: str, context: List[Dict] = None) -> str:
    """Função helper para chamar API do Manus"""
    if manus_integration is None:
        return "❌ Erro: Chave da API Manus não configurada."
        
    try:
        result = manus_integration.create_task(message, context)
        
        if "error" in result:
            return f"❌ Erro ao processar com Manus: {result['error']}"
        
        # A resposta real da API pode ser diferente. Vamos apenas imprimir o resultado completo
        print("\n--- RESPOSTA COMPLETA DA API ---")
        print(json.dumps(result, indent=2))
        print("-------------------------------")
        
        # Retorna uma mensagem de sucesso para a interface
        return "✅ Tarefa enviada com sucesso para o Manus. Verifique a resposta completa acima."
        
    except Exception as e:
        logger.error(f"Erro na integração com Manus: {e}")
        return f"❌ Erro na comunicação com Manus: {str(e)}"

# NOVO BLOCO DE EXECUÇÃO
if __name__ == "__main__":
    print("Iniciando o teste de integração com a API REAL do Manus...")
    
    if manus_integration is None:
        print("Teste não pode ser executado. Por favor, configure a variável de ambiente MANUS_API_KEY.")
    else:
        # Exemplo 1: Criar uma tarefa real de análise
        print("\nChamando a API para uma tarefa de 'análise'...")
        manus_response = manus_integration.create_task("Por favor, analise os dados de vendas do último trimestre.")
        print("Resposta da API Manus:")
        print(json.dumps(manus_response, indent=2))
        
        # Exemplo 2: Criar uma tarefa real de automação
        print("\nChamando a API para uma tarefa de 'automação'...")
        automacao_response = manus_integration.create_task("Automatizar o processo de envio de relatórios semanais.")
        print("Resposta da API Manus:")
        print(json.dumps(automacao_response, indent=2))

        # Exemplo 3: Listar as capacidades do Manus (esta parte não usa API real, é estática)
        print("\nListando as capacidades do Manus (informação estática)...")
        capabilities = manus_integration.list_capabilities()
        print(json.dumps(capabilities, indent=2))