import logging
import os

from dotenv import load_dotenv

load_dotenv()

try:
    from supabase import Client, create_client
except Exception:
    # não falhar na importação — funções abaixo lidarão com ausência do pacote
    create_client = None
    Client = None

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

logger = logging.getLogger("core.database")


def get_supabase_client() -> "Client | None":
    """Retorna um cliente Supabase se as credenciais e a biblioteca estiverem presentes.

    Em ambientes sem Supabase, retorna None para evitar que todo o sistema quebre.
    """
    if not create_client:
        logger.warning("Biblioteca 'supabase' não disponível no ambiente.")
        return None
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.warning("SUPABASE_URL ou SUPABASE_KEY não configurados.")
        return None
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        logger.error(f"Falha ao criar cliente Supabase: {e}")
        return None


if __name__ == "__main__":
    supabase = get_supabase_client()
    if supabase:
        print("Conexão com Supabase estabelecida com sucesso!")
    else:
        print("Supabase não configurado ou indisponível no ambiente.")
