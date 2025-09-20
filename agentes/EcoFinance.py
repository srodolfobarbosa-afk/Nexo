import os
from dotenv import load_dotenv
from core.database import get_supabase_client

load_dotenv()

class EcoFinanceAgent:
    def __init__(self):
        self.supabase = get_supabase_client()
        print("EcoFinanceAgent inicializado e conectado ao Supabase.")
        from core.api_search import APISearch
        self.api_search = APISearch()

    def run(self):
        print("EcoFinanceAgent está em execução...")
        # Aqui será implementada a lógica principal do agente EcoFinance
        # Por exemplo, monitoramento da economia interna, transações, etc.
        # Exemplo: self.monitor_economy()
        # Exemplo: self.process_transactions()

    def monitor_economy(self):
        print("Monitorando a economia interna...")
        # Lógica para monitorar dados econômicos

    def process_transactions(self):
        print("Processando transações...")
        # Lógica para processar transações financeiras

if __name__ == "__main__":
    agent = EcoFinanceAgent()
    agent.run()

