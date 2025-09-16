import os
import requests
import sys
import io
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, send_from_directory

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
            return None 
        return api_key
    except Exception as e:
        print(f"Erro: {e}")
        return None

@app.route("/")
def interface_chat():
    """
    Rota principal que serve a interface de chat
    """
    return send_from_directory("static", "index.html")



@app.route("/chat", methods=["POST"])
def processar_missao():
    """
    Rota para processar missões via chat
    """
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"response": "Por favor, envie uma mensagem válida."})
        
        # Importar e usar o fluxo de autoconstrução
        from scripts.generate_agent import main as generate_agent_main
        
        # Capturar a saída do console para retornar ao usuário
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            # Processar a missão usando o fluxo de autoconstrução
            # Por enquanto, rodamos em dry_run=True para testar a geração sem commitar
            generate_agent_main(user_message, dry_run=True)
            output = redirected_output.getvalue()
            return jsonify({"response": output})
        except Exception as e:
            output = redirected_output.getvalue()
            return jsonify({"response": f"Houve um erro ao processar a missão: {e}\nLogs: {output}"}), 500
        finally:
            sys.stdout = old_stdout
        
    except Exception as e:
        print(f"Erro ao processar missão: {e}")
        return jsonify({"response": f"Erro interno: {e}"}), 500


# Servir arquivos estáticos
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print("🌱 EcoGuardians - Sistema Iniciado")
    print("🤖 Nexo Gênesis - Agente Orquestrador Ativo")
    print(f"💬 Interface de Chat disponível em: http://127.0.0.1:{port}")
    app.run(debug=True, host="0.0.0.0", port=port)

