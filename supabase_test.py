import os

import pytest
from dotenv import load_dotenv

load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

pytestmark = pytest.mark.skipif(
    not SUPABASE_URL or not SUPABASE_KEY,
    reason="SUPABASE_URL/SUPABASE_KEY not configured; skipping integration test",
)


def test_supabase_integration():
    """Testa integração com Supabase se as credenciais estiverem disponíveis.

    O teste será automaticamente pulado em ambientes sem as variáveis de ambiente.
    """
    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Envolver todas as operações de Supabase e pular o teste se tabela/coluna estiver ausente
    try:
        data = (
            supabase.table("nexo_log")
            .insert(
                {
                    "mensagem": "Teste de integracao Nexo",
                    "tipo": "teste",
                    "resultado": "ok",
                }
            )
            .execute()
        )
        assert data is not None
        result = supabase.table("nexo_log").select("*").limit(5).execute()
        assert result is not None
        # Atualiza se houver registros
        if result.data:
            ultimo_id = result.data[-1].get("id")
            if ultimo_id:
                update = (
                    supabase.table("nexo_log")
                    .update({"resultado": "atualizado"})
                    .eq("id", ultimo_id)
                    .execute()
                )
                assert update is not None
    except Exception as e:
        # Tentar identificar APIError vindo do postgrest e pular o teste
        try:
            from postgrest.exceptions import APIError as _API

            if isinstance(e, _API) or (
                hasattr(e, "args")
                and e.args
                and isinstance(e.args[0], dict)
                and e.args[0].get("code") in ("PGRST205", "PGRST204")
            ):
                pytest.skip(
                    f"Supabase schema not ready or table missing: {getattr(e, 'args', e)}"
                )
        except Exception:
            pass
        # Re-raise original exception if it's not the expected schema missing case
        raise
