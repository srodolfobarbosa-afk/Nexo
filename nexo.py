import os
import requests
from dotenv import load_dotenv

def get_api_key():
    """
    Carrega e retorna a chave de API do arquivo .env.
    """
    try:
        load_dotenv()
        api_key = os.getenv("NEXO_API_KEY")
        if not api_key:
            raise ValueError("A variável NEXO_API_KEY não foi encontrada no arquivo .env")
        return api_key
    except ValueError as e:
        print(f"Erro: {e}")
        return None

def main():
    """
    Função principal que executa a lógica do programa.
    """
    print("Iniciando o programa...")
    api_key = get_api_key()

    if api_key:
        print("Chave de API carregada com sucesso!")
        # Aqui é onde você adicionaria a sua lógica para usar a API.
        # Por exemplo:
        # response = requests.get(f"https://api.exemplo.com?key={api_key}")
        # print(response.text)
    else:
        print("Não foi possível carregar a chave de API. Encerrando o programa.")

if __name__ == "__main__":
    main()