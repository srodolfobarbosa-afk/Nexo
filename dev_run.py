"""Entrypoint de desenvolvimento leve para facilitar execução local durante a auditoria.
Usa o app de `src.ws_server` se disponível; caso contrário inicia um servidor Flask mínimo.
"""
import os
import importlib

def run():
    try:
        mod = importlib.import_module("src.ws_server")
        app = getattr(mod, "app", None)
        if app is None:
            raise ImportError("src.ws_server.app não encontrado")
        print("Iniciando src.ws_server.app em modo debug na porta 8000")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)
    except Exception as e:
        print("Falha ao importar src.ws_server, iniciando fallback Flask simples:", e)
        from flask import Flask
        fapp = Flask("nexo_fallback")

        @fapp.route("/")
        def index():
            return {"status": "fallback", "message": "Nexo fallback running"}

        fapp.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8000)), debug=True)

if __name__ == "__main__":
    run()
