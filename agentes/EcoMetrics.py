from typing import Any, Dict, Optional
from core.memory import EcoMemory


class EcoMetrics:
    """Agente responsável por coletar e expor métricas do sistema.

    Usa EcoMemory para persistir eventos/metricas.
    """

    def __init__(self, memory: Optional[EcoMemory] = None):
        self.memory = memory or EcoMemory()

    def collect_metric(self, name: str, value: Any, meta: Optional[Dict[str, Any]] = None):
        payload = {"name": name, "value": value, "meta": meta or {}}
        self.memory.add_record(topic="metrics", payload=payload, tags=[name])

    def get_recent_metrics(self, limit: int = 100):
        recs = self.memory.query_recent(topic="metrics", limit=limit)
        # return simplified view
        return [r.get("payload") for r in recs]


if __name__ == "__main__":
    em = EcoMetrics()
    em.collect_metric("cpu", 12.5, {"unit": "%"})
    print(em.get_recent_metrics())
