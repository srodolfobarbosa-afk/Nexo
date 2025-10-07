import logging
import os

from dotenv import load_dotenv

from core.database import get_supabase_client

load_dotenv()


class EcoFinanceAgent:
    """Agente de finanças responsável por gerenciar receitas e auditoria."""

    def __init__(self, nl_handler=None):
        self.supabase = get_supabase_client()
        self.nl = nl_handler
        logging.info("EcoFinanceAgent inicializado e conectado ao Supabase.")

    def run(self):
        logging.info("EcoFinanceAgent está em execução...")
        # Fluxo simples de demonstração: analisar saldo, registrar auditoria
        try:
            balance = self.get_balance()
            logging.info(f"Saldo atual: {balance}")
            self.log_audit("run", {"balance": balance})
        except Exception as e:
            logging.exception("Erro durante execução do EcoFinanceAgent")

    def get_balance(self) -> float:
        # Implementação mínima: buscar soma de registros de transações na tabela `transactions`
        try:
            resp = self.supabase.table("transactions").select("amount").execute()
            rows = resp.data or []
            total = sum([r.get("amount", 0) for r in rows])
            return float(total)
        except Exception:
            logging.exception("Falha ao calcular balance")
            return 0.0

    def record_transaction(self, amount: float, metadata: dict | None = None):
        metadata = metadata or {}
        try:
            self.supabase.table("transactions").insert(
                {"amount": amount, "metadata": metadata}
            ).execute()
            self.log_audit(
                "transaction_recorded", {"amount": amount, "metadata": metadata}
            )
        except Exception:
            logging.exception("Falha ao registrar transação")

    def log_audit(self, action: str, details: dict):
        try:
            self.supabase.table("audit_logs").insert(
                {"action": action, "details": details}
            ).execute()
        except Exception:
            logging.exception("Falha ao gravar log de auditoria")


if __name__ == "__main__":
    from core.nl_handler import NLHandler

    nl = NLHandler()
    agent = EcoFinanceAgent(nl)
    agent.run()
