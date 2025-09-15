import os
import pytest
from dotenv import load_dotenv

def test_dotenv_carregado():
    """
    Testa se o arquivo .env é carregado corretamente.
    """
    # Garante que as variáveis de ambiente não estão no sistema antes do teste
    if 'NEXO_API_KEY' in os.environ:
        del os.environ GEMINI_API_KEY=AIzaSyB7uJGYZlanQ-39ZhYS6ndk69HZik8lO98
    
    # Carrega o arquivo .env (assumindo que ele está no mesmo diretório)
    load_dotenv()
    
    # Assert é a "afirmação" do teste. Se for falsa, o teste falha.
    assert 'NEXO_API_KEY' in os.environ, "A variável NEXO_API_KEY não foi carregada do .env."