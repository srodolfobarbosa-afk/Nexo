import os
import pytest
from dotenv import load_dotenv
from core.database import get_supabase_client
from agentes.EcoFinance import EcoFinanceAgent

def test_dotenv_carregado():
    """
    Testa se o arquivo .env é carregado corretamente e contém as chaves esperadas.
    """
    # Garante que as variáveis de ambiente não estão no sistema antes do teste
    if 'SUPABASE_URL' in os.environ:
        del os.environ['SUPABASE_URL']
    if 'SUPABASE_KEY' in os.environ:
        del os.environ['SUPABASE_KEY']
    if 'GEMINI_API_KEY' in os.environ:
        del os.environ['GEMINI_API_KEY']
    if 'OPENAI_API_KEY' in os.environ:
        del os.environ['OPENAI_API_KEY']
    
    # Carrega o arquivo .env
    load_dotenv()
    
    # Verifica se as chaves de API foram carregadas
    assert 'SUPABASE_URL' in os.environ, "A variável SUPABASE_URL não foi carregada do .env."
    assert 'SUPABASE_KEY' in os.environ, "A variável SUPABASE_KEY não foi carregada do .env."
    assert 'GEMINI_API_KEY' in os.environ, "A variável GEMINI_API_KEY não foi carregada do .env."
    assert 'OPENAI_API_KEY' in os.environ, "A variável OPENAI_API_KEY não foi carregada do .env."

def test_ecofinance_agent_initialization():
    """
    Testa a inicialização do EcoFinanceAgent e a conexão com o Supabase.
    """
    load_dotenv()
    agent = EcoFinanceAgent()
    assert agent.supabase is not None, "EcoFinanceAgent não conseguiu se conectar ao Supabase."
    print("EcoFinanceAgent inicializado e conectado ao Supabase com sucesso.")

