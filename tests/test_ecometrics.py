import os
import tempfile
from agentes.EcoMetrics import EcoMetrics
from core.memory import EcoMemory


def test_collect_and_query():
    # use a temporary sqlite file to avoid polluting workspace
    tmp = tempfile.NamedTemporaryFile(delete=False)
    path = tmp.name
    tmp.close()

    mem = EcoMemory(db_path=path)
    em = EcoMetrics(memory=mem)
    em.collect_metric("test_metric", 42, {"note": "unit test"})

    metrics = em.get_recent_metrics(limit=10)
    assert any(m.get("name") == "test_metric" and m.get("value") == 42 for m in metrics)

    # cleanup
    try:
        os.unlink(path)
    except Exception:
        pass
