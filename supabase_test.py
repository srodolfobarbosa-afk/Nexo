import os
from dotenv import load_dotenv
import pytest

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

pytestmark = pytest.mark.skipif(not SUPABASE_URL or not SUPABASE_KEY, reason="SUPABASE_URL/SUPABASE_KEY not configured; skipping integration test")


def test_supabase_integration():
    """Testa integração com Supabase se as credenciais estiverem disponíveis.

    O teste será automaticamente pulado em ambientes sem as variáveis de ambiente.
    """
    from supabase import create_client

    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
    # Tenta inserir, ler e atualizar um registro de exemplo
    data = supabase.table('nexo_log').insert({'mensagem': 'Teste de integração Nexo', 'tipo': 'teste', 'resultado': 'ok'}).execute()
    assert data is not None
    result = supabase.table('nexo_log').select('*').limit(5).execute()
    assert result is not None
    # Atualiza se houver registros
    if result.data:
        ultimo_id = result.data[-1].get('id')
        if ultimo_id:
            update = supabase.table('nexo_log').update({'resultado': 'atualizado'}).eq('id', ultimo_id).execute()
            assert update is not None

