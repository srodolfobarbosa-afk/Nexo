
import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_supabase_client():
    import core.supabase_client as sc
    assert hasattr(sc, "save_memory")
    assert hasattr(sc, "save_task")

