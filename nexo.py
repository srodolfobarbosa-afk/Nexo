import os
import requests
from dotenv import load_dotenv
from flask import Flask

# Cria a sua aplicação Flask
app = Flask(__name__)

def get_api_key():
    """
    Carrega e retorna a chave de API do arquivo .env.
    """
    try:
        load_dotenv()
        api_key = os.getenv("NEXO_API_KEY")
        if not api_key:
            # Agora que estamos em um servidor web, esta lógica é menos necessária
            # mas é bom ter para testes locais
            return None 
        return api_key
    except Exception as e:
        print(f"Erro: {e}")
        return None

@app.route("/")
def iniciar_agente():
    """
    Uma rota que inicia a tarefa do agente de IA.
    """
    print("Iniciando o programa...")
    api_key = get_api_key()

    if api_key:
        print("Chave de API carregada com sucesso!")
        # Aqui é onde você vai colocar a sua lógica principal do agente de IA.
        # Essa função precisa ser capaz de rodar por muito tempo.
        return "Agente de IA iniciado com sucesso!"
    else:
        print("Não foi possível carregar a chave de API.")
        return "Erro: Não foi possível carregar a chave de API.", 500

if __name__ == "__main__":
    # Esta parte é para testar a aplicação no seu computador
    app.run(debug=True)