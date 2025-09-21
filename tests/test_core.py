def test_supabase_client():
    import core.supabase_client as sc
    assert hasattr(sc, "save_memory")
    assert hasattr(sc, "save_task")

