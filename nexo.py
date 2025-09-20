import os
import requests
import io
import sys
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

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
        
        from core.auto_construction import AutoConstructionModule
        # Instanciar o módulo de auto-construção
        def llm_caller(prompt, context):
            # Aqui você pode integrar com seu LLM real
            return '{"overview": "Missão processada", "components": ["auto"]}'
        auto_constructor = AutoConstructionModule(llm_caller)
        
        # Capturar a saída do console para retornar ao usuário
        old_stdout = sys.stdout
        redirected_output = io.StringIO()
        sys.stdout = redirected_output

        try:
            # Processar a missão usando o AutoConstructionModule
            result = auto_constructor.auto_construct_feature(user_message)
            output = redirected_output.getvalue()
            return jsonify({"response": f"Resultado da missão: {result}\nLogs: {output}"})
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

# Registrar rotas da API para integração com Telegram
try:
    from api_endpoints import register_api_routes
    register_api_routes(app)
    print("✅ Rotas da API do Telegram registradas")
except ImportError as e:
    print(f"⚠️ Não foi possível carregar rotas da API: {e}")

def auto_evolution_persistente(missao, max_retries=9999, cooldown=30):
    """
    Função para tentar processar uma missão várias vezes em caso de falha,
    com um tempo de espera (cooldown) entre as tentativas.
    """
    from core.auto_construction import AutoConstructionModule
    def llm_caller(prompt, context):
        # Aqui você pode integrar com seu LLM real
        return '{"overview": "Missão processada", "components": ["auto"]}'
    auto_constructor = AutoConstructionModule(llm_caller)
    tentativas = 0
    while tentativas < max_retries:
        try:
            print(f"[Nexo] Tentativa {tentativas+1} de auto-evolução para missão: {missao}")
            result = auto_constructor.auto_construct_feature(missao)
            print(f"[Nexo] Missão concluída: {result}")
            return result
        except Exception as e:
            print(f"[Nexo] Erro na missão: {e}. Entrando em modo de auto-correção. Nova tentativa em {cooldown} segundos...")
            time.sleep(cooldown)
            tentativas += 1
    print("[Nexo] Limite de tentativas atingido. Missão não concluída.")
    return None

@app.route("/agentes-log")
def agentes_log():
    # Lê registros da memória local (memoria_curto_prazo.json)
    memoria_path = os.path.join(os.path.dirname(__file__), 'memoria_curto_prazo.json')
    if not os.path.exists(memoria_path):
        return jsonify([])
    try:
        with open(memoria_path, 'r') as f:
            dados = json.load(f)
        # Extrai registros de ferramentas e outras ações
        logs = []
        if 'ferramentas' in dados:
            for nome, info in dados['ferramentas'].items():
                entry = info.copy()
                entry['nome'] = nome
                logs.append(entry)
        # Adicione outros tipos de registro se necessário
        return jsonify(logs)
    except Exception as e:
        return jsonify({'erro': str(e)})

@app.route("/agentes_log.html")
def agentes_log_html():
    return send_from_directory("static", "agentes_log.html")

if __name__ == "__main__":
    import socket
    def find_free_port(start_port=5000, max_tries=10):
        port = start_port
        for _ in range(max_tries):
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                if s.connect_ex(("127.0.0.1", port)) != 0:
                    return port
                port += 1
        raise RuntimeError("Não há portas livres disponíveis.")

    port = find_free_port(int(os.environ.get("PORT", 5000)))
    print("🌱 EcoGuardians - Sistema Iniciado")
    print("🤖 Nexo Gênesis - Agente Orquestrador Ativo")
    print(f"💬 Interface de Chat disponível em: http://127.0.0.1:{port}")
    print("🤖 API do Telegram Bot integrada")
    app.run(debug=True, host="0.0.0.0", port=port)

