
from flask import Flask, jsonify, send_from_directory
import sys
import os
import threading
from flask import request, abort
import shutil

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
    # Habilitar loop de auto-evolução em background quando a variável de ambiente
    # START_AUTO_EVOLUTION estiver definida como '1' ou 'true'.
    # Para deploy automático controlado pelo AutoConstructionModule, defina
    # AUTO_CONSTRUCTION_ALLOW_DEPLOY=1 (use com cautela).
    if len(sys.argv) > 1 and sys.argv[1] == "auto-evolution":
        # Modo legado: executar em foreground
        sys.path.append("..")
        from auto_evolution_loop import auto_evolution_loop
        auto_evolution_loop()
    else:
        # Iniciar loop de auto-evolução em background (daemon thread) para não
        # bloquear o servidor WSGI; apenas quando explicitamente solicitado.
        start_auto = os.environ.get('START_AUTO_EVOLUTION', os.environ.get('START_AUTO_CONSTRUCTION', '0'))
        if str(start_auto).lower() in ('1', 'true', 'yes'):
            try:
                sys.path.append("..")
                from auto_evolution_loop import auto_evolution_loop

                def _run_auto_loop():
                    try:
                        auto_evolution_loop()
                    except Exception as e:
                        print(f"[auto_evolution] erro no loop: {e}")

                t = threading.Thread(target=_run_auto_loop, daemon=True)
                t.start()
                print("[startup] auto_evolution_loop iniciado em background (daemon thread).")
            except Exception as e:
                print(f"[startup] falha ao iniciar auto_evolution_loop: {e}")

        app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))

    # Endpoints administrativos leves (somente no modo __main__ para evitar expor via WSGI inadvertently)
    # Nota: em produção, proteja isso melhor (HTTPS, auth robusta, IP allowlist)
    @app.route('/admin/staged_builds', methods=['GET'])
    def list_staged_builds():
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        staging_root = os.path.join(repo_root, 'autoconstruct_staging')
        if not os.path.exists(staging_root):
            return jsonify({'staged': []})
        items = []
        for name in os.listdir(staging_root):
            meta = {}
            meta_path = os.path.join(staging_root, name, 'meta.json')
            if os.path.exists(meta_path):
                try:
                    import json
                    with open(meta_path, 'r', encoding='utf-8') as mf:
                        meta = json.load(mf)
                except Exception:
                    meta = {'staged_id': name}
            else:
                meta = {'staged_id': name}
            items.append(meta)
        return jsonify({'staged': items})

    @app.route('/admin/apply_staged/<staged_id>', methods=['POST'])
    def apply_staged_build(staged_id):
        token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('admin_token')
        if not token or token != os.environ.get('ADMIN_DEPLOY_TOKEN'):
            abort(403)
        repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        staging_dir = os.path.join(repo_root, 'autoconstruct_staging', staged_id)
        if not os.path.exists(staging_dir):
            return jsonify({'error': 'staged_not_found'}), 404

        # Copiar arquivos do staging para o repo
        for root, dirs, files in os.walk(staging_dir):
            rel = os.path.relpath(root, staging_dir)
            for f in files:
                if f == 'meta.json':
                    continue
                src = os.path.join(root, f)
                dest = os.path.join(repo_root, rel, f) if rel != '.' else os.path.join(repo_root, f)
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(src, dest)

        # Commit se permitido
        allow_deploy = str(os.environ.get('AUTO_CONSTRUCTION_ALLOW_DEPLOY', '0')).lower() in ('1', 'true', 'yes')
        commit_result = None
        try:
            if allow_deploy:
                import subprocess
                subprocess.run('git add .', shell=True, cwd=repo_root)
                subprocess.run(f'git commit -m "Applied staged build {staged_id}"', shell=True, cwd=repo_root)
                commit_result = 'committed'
            else:
                commit_result = 'staged_copied'
        except Exception as e:
            commit_result = f'error: {e}'

        return jsonify({'status': 'applied', 'staged_id': staged_id, 'commit': commit_result})
