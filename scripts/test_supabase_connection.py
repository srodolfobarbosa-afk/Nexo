import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

def check_supabase_connection():
    """
    Verifica a conexão com o Supabase usando as credenciais do ambiente.
    """
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        print("❌ As variáveis de ambiente SUPABASE_URL e SUPABASE_KEY não foram definidas.")
        return

    print(f"🔌 Tentando conectar ao Supabase URL: {supabase_url[:20]}...")

    try:
        supabase: Client = create_client(supabase_url, supabase_key)

        # Tentativa de fazer uma query simples na tabela usada pelo EcoMemory: 'memory'
        try:
            response = supabase.table("memory").select("id").limit(1).execute()
            print("✅ Conexão com o Supabase bem-sucedida!")
            print("🔍 Resposta da query de teste:", response.data)
        except Exception as e:
            # Mensagem útil quando a tabela não existe ou há problema de permissão
            msg = str(e)
            print(f"❌ Erro ao consultar a tabela 'memory': {msg}")
            print("Dica: crie a tabela 'memory' no schema public. Exemplo SQL:")
            print('\n-- Habilitar extensão para gen_random_uuid (se desejar)\nCREATE EXTENSION IF NOT EXISTS "pgcrypto";\n\n-- Criação mínima da tabela memory\nCREATE TABLE public.memory (\n  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),\n  topic text NOT NULL,\n  payload jsonb NOT NULL,\n  tags jsonb,\n  sentiment text,\n  created_at timestamptz DEFAULT now()\n);\n')
            return

    except Exception as e:
        print(f"❌ Falha ao conectar ou fazer query no Supabase: {e}")

if __name__ == "__main__":
    check_supabase_connection()
