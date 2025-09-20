import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception('SUPABASE_URL ou SUPABASE_KEY não encontrados no .env')

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def testar_supabase():
    print('Testando integração com Supabase usando a tabela nexo_log...')
    try:
        # Insere um registro de teste
        data = supabase.table('nexo_log').insert({'mensagem': 'Teste de integração Nexo', 'tipo': 'teste', 'resultado': 'ok'}).execute()
        print('Registro inserido:', data)
        # Consulta todos os registros
        result = supabase.table('nexo_log').select('*').execute()
        print('Registros encontrados:', result.data)
        # Atualiza o último registro inserido (exemplo)
        if result.data:
            ultimo_id = result.data[-1]['id']
            update = supabase.table('nexo_log').update({'resultado': 'atualizado'}).eq('id', ultimo_id).execute()
            print('Registro atualizado:', update)
    except Exception as e:
        print('Erro ao testar Supabase:', e)

if __name__ == "__main__":
    testar_supabase()
