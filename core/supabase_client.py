import os
import logging
from typing import Optional

logger = logging.getLogger("supabase_client")

from .database import get_supabase_client as core_get_supabase_client


def get_supabase_client() -> Optional[object]:
    try:
        return core_get_supabase_client()
    except Exception as e:
        logger.error(f"Erro ao obter cliente Supabase: {e}")
        return None


def save_memory(table_name: str, data: dict):
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase indisponível — save_memory ignorado.")
        return
    try:
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Memória salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar memória na tabela {table_name}: {e}")


def save_task(table_name: str, data: dict):
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase indisponível — save_task ignorado.")
        return
    try:
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Tarefa salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar tarefa na tabela {table_name}: {e}")


def save_log(level: str, message: str, details: dict = None):
    supabase = get_supabase_client()
    if not supabase:
        logger.warning(f"Supabase indisponível — log não persistido: {message}")
        return
    try:
        log_entry = {"level": level, "message": message, "details": details}
        supabase.table("agent_logs").insert(log_entry).execute()
        logger.info(f"Log salvo no Supabase: {message}")
    except Exception as e:
        logger.error(f"Erro ao salvar log no Supabase: {e}")

