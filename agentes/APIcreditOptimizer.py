import logging
from core.database import get_supabase_client
from datetime import datetime

logger = logging.getLogger(__name__)

class APIcreditOptimizer:
    """
    Agente responsável por monitorar e otimizar o uso de créditos de APIs.
    """

    def __init__(self):
        self.supabase = get_supabase_client()
        logger.info("🔎 APIcreditOptimizer inicializado.")

    def analyze_usage(self):
        """
        Analisa o uso de créditos no Supabase e retorna recomendações.
        """
        try:
            response = (
                self.supabase.table("api_usage")
                .select("*")
                .order("timestamp", desc=True)
                .limit(50)
                .execute()
            )

            if not response.data:
                return "Nenhum dado de uso encontrado."

            # Exemplo simples: contar chamadas por provedor
            usage_summary = {}
            for row in response.data:
                provider = row.get("provider", "desconhecido")
                usage_summary[provider] = usage_summary.get(provider, 0) + 1

            return f"Resumo de uso de APIs: {usage_summary}"

        except Exception as e:
            logger.error(f"Erro ao analisar uso de APIs: {e}")
            return f"Erro ao analisar uso de APIs: {e}"

    def suggest_optimization(self):
        """
        Sugere otimizações de uso de créditos.
        """
        try:
            usage_report = self.analyze_usage()

            if isinstance(usage_report, str):
                return usage_report

            suggestions = []
            for provider, count in usage_report.items():
                if count > 100:
                    suggestions.append(
                        f"O provedor {provider} está sendo muito usado ({count} chamadas). Considere alternar para outro LLM."
                    )
                else:
                    suggestions.append(
                        f"O provedor {provider} está com uso controlado ({count} chamadas)."
                    )

            return "\n".join(suggestions)

        except Exception as e:
            logger.error(f"Erro ao sugerir otimizações: {e}")
            return f"Erro ao sugerir otimizações: {e}"

    def log_action(self, action: str, details: dict):
        """
        Salva uma ação do agente no Supabase para auditoria.
        """
        try:
            self.supabase.table("agent_logs").insert(
                {
                    "agent": "APIcreditOptimizer",
                    "action": action,
                    "details": details,
                    "timestamp": datetime.now().isoformat(),
                }
            ).execute()
            logger.info(f"Ação registrada: {action}")
        except Exception as e:
            logger.error(f"Erro ao salvar log de ação: {e}")