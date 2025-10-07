import logging
import os
from typing import Optional

logger = logging.getLogger("supabase_client")

from . import sqlite_client
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
        logger.warning("Supabase indisponível — gravando em SQLite local.")
        try:
            sqlite_client.save_memory_local(table_name, str(data))
        except Exception as e:
            logger.error(f"Erro salvando memória local: {e}")
        return
    try:
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Memória salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar memória na tabela {table_name}: {e}")


def save_task(table_name: str, data: dict):
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase indisponível — gravando tarefa em SQLite local.")
        try:
            sqlite_client.save_task_local(
                data.get("name", "task"),
                status=data.get("status", "pending"),
                result=str(data.get("result", "")),
                reward=float(data.get("reward", 0.0)),
            )
        except Exception as e:
            logger.error(f"Erro salvando task local: {e}")
        return
    try:
        supabase.table(table_name).insert(data).execute()
        logger.info(f"Tarefa salva na tabela {table_name}.")
    except Exception as e:
        logger.error(f"Erro ao salvar tarefa na tabela {table_name}: {e}")


def save_log(level: str, message: str, details: dict = None):
    supabase = get_supabase_client()
    if not supabase:
        logger.warning(f"Supabase indisponível — gravando log local: {message}")
        try:
            sqlite_client.save_log_local(
                level, message, str(details) if details else None
            )
        except Exception as e:
            logger.error(f"Erro salvando log local: {e}")
        return
    try:
        log_entry = {"level": level, "message": message, "details": details}
        supabase.table("agent_logs").insert(log_entry).execute()
        logger.info(f"Log salvo no Supabase: {message}")
    except Exception as e:
        logger.error(f"Erro ao salvar log no Supabase: {e}")
