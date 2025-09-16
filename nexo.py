import os
import requests
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
            # Agora que estamos em um servidor web, esta lógica é menos necessária
            # mas é bom ter para testes locais
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
    return send_from_directory('static', 'index.html')

@app.route("/iniciar")
def iniciar_agente():
    """
    Uma rota que inicia a tarefa do agente de IA.
    """
    print("Iniciando o programa...")
    print("Iniciando o agente EcoFinance...")
    from agentes.EcoFinance import EcoFinanceAgent
    agent = EcoFinanceAgent()
    agent.run()
    return "Agente EcoFinance iniciado com sucesso!"

@app.route("/chat", methods=["POST"])
def processar_missao():
    """
    Rota para processar missões via chat
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '')
        
        if not user_message:
            return jsonify({"response": "Por favor, envie uma mensão válida."})
        
        # Importar e usar o Nexo Gênesis
        from agentes.NexoGenesis import NexoGenesisAgent
        nexo = NexoGenesisAgent()
        
        # Processar a missão
        response = nexo.process_mission(user_message)
        
        return jsonify({"response": response})
        
    except Exception as e:
        print(f"Erro ao processar missão: {e}")
        return jsonify({"response": f"Erro interno: {e}"}), 500

@app.route("/status")
def status_sistema():
    """
    Rota para verificar o status do sistema
    """
    try:
        from agentes.NexoGenesis import NexoGenesisAgent
        nexo = NexoGenesisAgent()
        status = nexo.get_status()
        return jsonify(status)
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

@app.route("/agentes")
def listar_agentes():
    """
    Rota para listar agentes disponíveis
    """
    try:
        import glob
        agentes_files = glob.glob("agentes/*.py")
        agentes = []
        
        for file in agentes_files:
            if "__" not in file:  # Ignorar __pycache__ e __init__.py
                nome = os.path.basename(file).replace('.py', '')
                agentes.append(nome)
        
        return jsonify({"agentes": agentes})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

# Servir arquivos estáticos
@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory('static', filename)

if __name__ == "__main__":
    # Esta parte é para testar a aplicação no seu computador
    print("🌱 EcoGuardians - Sistema Iniciado")
    print("🤖 Nexo Gênesis - Agente Orquestrador Ativo")
    print("💬 Interface de Chat disponível em: http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
