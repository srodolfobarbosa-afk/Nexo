import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

def get_supabase_client() -> Client:
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

# Exemplo de uso (pode ser removido ou adaptado conforme necessário)
if __name__ == "__main__":
    try:
        supabase = get_supabase_client()
        print("Conexão com Supabase estabelecida com sucesso!")
        # Exemplo de consulta
        # response = supabase.table("your_table_name").select("*").execute()
        # print(response.data)
    except ValueError as e:
        print(f"Erro de configuração: {e}")
    except Exception as e:
        print(f"Ocorreu um erro ao conectar ou consultar o Supabase: {e}")

