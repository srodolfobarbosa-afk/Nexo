import logging
from typing import Any, Dict, Optional

from core.database import get_supabase_client

logger = logging.getLogger("supabase_adapter")


def insert(table: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase not configured; insert skipped")
        return None
    try:
        res = supabase.table(table).insert(data).execute()
        return res.data if hasattr(res, "data") else None
    except Exception:
        logger.exception("Supabase insert failed")
        return None


def select(table: str, query: Dict[str, Any]) -> Optional[Any]:
    supabase = get_supabase_client()
    if not supabase:
        logger.warning("Supabase not configured; select returns None")
        return None
    try:
        q = supabase.table(table)
        # simple filters
        for k, v in query.items():
            q = q.eq(k, v)
        res = q.select("*").execute()
        return res.data if hasattr(res, "data") else None
    except Exception:
        logger.exception("Supabase select failed")
        return None
