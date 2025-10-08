import os
import sqlite3
import json
from typing import Optional, Dict, Any

try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except Exception:
    SUPABASE_AVAILABLE = False


class StarterAgent:
    """Agente inicial leve.

    Comportamento:
    - Se encontrar variáveis SUPABASE_URL / SUPABASE_KEY e a biblioteca supabase estiver instalada,
      usa Supabase para persistência.
    - Caso contrário, persiste localmente em `data/starter_agent.db` (SQLite).
    - Possui método `ask` que devolve uma resposta simples (echo/fallback) para testes.
    """

    def __init__(self, db_path: str = "data/starter_agent.db"):
        self.supabase_url = os.environ.get("SUPABASE_URL")
        self.supabase_key = os.environ.get("SUPABASE_KEY")
        self.use_supabase = bool(self.supabase_url and self.supabase_key and SUPABASE_AVAILABLE)
        if self.use_supabase:
            self.sb = create_client(self.supabase_url, self.supabase_key)
        else:
            os.makedirs(os.path.dirname(db_path), exist_ok=True)
            self.conn = sqlite3.connect(db_path)
            self._ensure_tables()

    def _ensure_tables(self):
        cur = self.conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                meta TEXT
            )
            """
        )
        self.conn.commit()

    def save_message(self, role: str, content: str, meta: Optional[Dict[str, Any]] = None):
        meta_json = json.dumps(meta or {})
        if self.use_supabase:
            self.sb.table("messages").insert({"role": role, "content": content, "meta": meta_json}).execute()
        else:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO messages (role, content, meta) VALUES (?, ?, ?)", (role, content, meta_json))
            self.conn.commit()

    def history(self, limit: int = 50):
        if self.use_supabase:
            resp = self.sb.table("messages").select("*").order("id", desc=False).limit(limit).execute()
            return resp.data
        else:
            cur = self.conn.cursor()
            cur.execute("SELECT id, role, content, meta FROM messages ORDER BY id ASC LIMIT ?", (limit,))
            rows = cur.fetchall()
            return [
                {"id": r[0], "role": r[1], "content": r[2], "meta": json.loads(r[3] or "{}")}
                for r in rows
            ]

    def ask(self, prompt: str) -> str:
        """Simplesmente retorna um echo com algumas heurísticas de fallback.

        Se no futuro quiser conectar a LLMs, substitua essa função por uma chamada à cadeia de providers.
        """
        # save user message
        self.save_message("user", prompt)
        # heurística simples: se detectar palavra-chave, responder de forma específica
        p = prompt.strip().lower()
        if "help" in p or "ajuda" in p:
            answer = "Posso ajudar com tarefas: criar missão, verificar status, listar oportunidades."
        elif "ping" in p:
            answer = "pong"
        else:
            # echo curto
            answer = f"Recebi: {prompt[:200]}"
        # save assistant message
        self.save_message("assistant", answer)
        return answer


if __name__ == "__main__":
    a = StarterAgent()
    print(a.ask("ping"))
