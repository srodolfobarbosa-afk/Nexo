import os
import logging
import requests

class APIcreditOptimizer:
    """
    Classe responsável por monitorar e otimizar o uso de créditos de API.
    - Verifica saldo disponível.
    - Alterna entre provedores (OpenAI, Gemini, Groq).
    - Faz fallback automático em caso de erro.
    """

    def __init__(self):
        self.providers = {
            "openai": os.getenv("OPENAI_API_KEY"),
            "gemini": os.getenv("GEMINI_API_KEY"),
            "groq": os.getenv("GROQ_API_KEY"),
        }
        self.active_provider = None
        self.logger = logging.getLogger("APIcreditOptimizer")

    def select_provider(self):
        """
        Seleciona automaticamente um provedor válido com base na chave de API disponível.
        """
        for name, key in self.providers.items():
            if key and key != "None":
                self.active_provider = name
                self.logger.info(f"✅ Provedor selecionado: {name}")
                return name
        self.logger.error("❌ Nenhum provedor válido encontrado.")
        return None

    def check_balance(self, provider):
        """
        Exemplo de verificação de créditos (mock).
        Em produção, cada provedor terá sua API real de billing.
        """
        if provider == "openai":
            return {"status": "ok", "credits": 100}
        elif provider == "gemini":
            return {"status": "ok", "credits": 200}
        elif provider == "groq":
            return {"status": "ok", "credits": 150}
        else:
            return {"status": "error", "credits": 0}

    def optimize(self):
        """
        Otimiza o uso de API escolhendo o provedor com mais créditos.
        """
        best_provider = None
        max_credits = -1

        for provider in self.providers.keys():
            balance = self.check_balance(provider)
            if balance["status"] == "ok" and balance["credits"] > max_credits:
                best_provider = provider
                max_credits = balance["credits"]

        if best_provider:
            self.active_provider = best_provider
            self.logger.info(f"🚀 Alternando para {best_provider} (créditos: {max_credits})")
        else:
            self.logger.error("❌ Nenhum provedor disponível para otimização.")
        return self.active_provider

