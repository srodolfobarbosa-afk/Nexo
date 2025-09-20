
from flask import Flask, jsonify, send_from_directory
import sys

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")

@app.route("/")
def home():
    try:
        return send_from_directory(app.static_folder, 'index.html')
    except Exception:
        return "EcoGuardians (minimal) — index missing", 200

@app.route("/status")
def status():
    return jsonify({
        "service":"EcoGuardians (minimal)",
        "status":"online",
        "notes":"API mínima criada. Substitua por sua aplicação real."
    })

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "auto-evolution":
        import sys
        sys.path.append("..")
        from auto_evolution_loop import auto_evolution_loop
        auto_evolution_loop()
    else:
        app.run(host="0.0.0.0", port=5000)
