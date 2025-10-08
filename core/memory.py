import os
import sqlite3
import json
from typing import Any, Dict, List, Optional

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False
import logging


class EcoMemory:
    """Memória compartilhada entre agentes.

    Usa Supabase (se configurado) ou SQLite local (data/eco_memory.db) como fallback.
    Registra eventos/experiências com campos: topic, payload, tags, sentiment, timestamp.
    """

    def __init__(self, db_path: str = "data/eco_memory.db"):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        # prefer supabase se disponível e configurado, mas faça fallback seguro para sqlite
        self.use_supabase = False
        self.sb = None
        if self.supabase_url and self.supabase_key and SUPABASE_AVAILABLE:
            try:
                self.sb = create_client(self.supabase_url, self.supabase_key)
                # faça uma chamada simples para validar cliente
                # (nem sempre disponível, mas evita crashes posteriores)
                try:
                    # list tables minimalmente (pode falhar se não houver permissão)
                    _ = self.sb.table('memory')
                    self.use_supabase = True
                except Exception:
                    logging.warning("Supabase client inicializado, mas validação falhou; usando SQLite fallback")
                    self.use_supabase = False
            except Exception as e:
                logging.warning(f"Falha ao inicializar Supabase client: {e}; usando SQLite fallback")

        if not self.use_supabase:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path, check_same_thread=False)
            self._ensure_table()

    def _ensure_table(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                payload TEXT NOT NULL,
                tags TEXT,
                sentiment TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        self.conn.commit()

    def add_record(self, topic: str, payload: Dict[str, Any], tags: Optional[List[str]] = None, sentiment: Optional[str] = None):
        payload_json = json.dumps(payload)
        tags_json = json.dumps(tags or [])
        if self.use_supabase:
            self.sb.table("memory").insert({"topic": topic, "payload": payload_json, "tags": tags_json, "sentiment": sentiment}).execute()
        else:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO memory (topic, payload, tags, sentiment) VALUES (?, ?, ?, ?)", (topic, payload_json, tags_json, sentiment))
            self.conn.commit()

    def query_recent(self, topic: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        if self.use_supabase:
            q = self.sb.table("memory").select("*").order("created_at", desc=True).limit(limit)
            if topic:
                q = q.eq("topic", topic)
            resp = q.execute()
            return resp.data
        else:
            cur = self.conn.cursor()
            if topic:
                cur.execute("SELECT id, topic, payload, tags, sentiment, created_at FROM memory WHERE topic=? ORDER BY created_at DESC LIMIT ?", (topic, limit))
            else:
                cur.execute("SELECT id, topic, payload, tags, sentiment, created_at FROM memory ORDER BY created_at DESC LIMIT ?", (limit,))
            rows = cur.fetchall()
            out = []
            for r in rows:
                out.append({
                    "id": r[0],
                    "topic": r[1],
                    "payload": json.loads(r[2] or "{}"),
                    "tags": json.loads(r[3] or "[]"),
                    "sentiment": r[4],
                    "created_at": r[5],
                })
            return out

    def summarize_topic(self, topic: str, max_records: int = 50) -> str:
        # lightweight summarization: concatenate payloads up to limit
        recs = self.query_recent(topic=topic, limit=max_records)
        texts = [json.dumps(r.get("payload", {})) for r in recs]
        joined = "\n".join(texts)
        if len(joined) > 2000:
            return joined[:2000] + "..."
        return joined
