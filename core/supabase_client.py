import os
import logging
from supabase import create_client, Client

logger = logging.getLogger("supabase_client")

def get_supabase_client() -> Client:
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")
    if not supabase_url or not supabase_key:
        logger.error("SUPABASE_URL ou SUPABASE_KEY não configurados para SupabaseClient.")
        raise ValueError("Credenciais Supabase não configuradas.")
    return create_client(supabase_url, supabase_key)

def save_memory(table_name: str, data: dict):
    try:
        supabase = get_supabase_client()
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Memória salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar memória na tabela {table_name}: {e}")

def save_task(table_name: str, data: dict):
    try:
        supabase = get_supabase_client()
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Tarefa salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar tarefa na tabela {table_name}: {e}")

def save_log(level: str, message: str, details: dict = None):
    try:
        supabase = get_supabase_client()
        log_entry = {"level": level, "message": message, "details": details}
        supabase.table("agent_logs").insert(log_entry).execute()
        logger.info(f"Log salvo no Supabase: {message}")
    except Exception as e:
        logger.error(f"Erro ao salvar log no Supabase: {e}")

