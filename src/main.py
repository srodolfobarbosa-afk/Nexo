
from flask import Flask, jsonify, send_from_directory
import sys
import os
import threading
from flask import request, abort
import shutil

app = Flask(__name__, static_folder="../app/static", static_url_path="/static")
# Autonomy control state (in-memory)
_autonomy_thread = None
_autonomy_running = False

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


@app.route('/ecobank/balance/<account_id>')
def ecobank_balance(account_id):
    try:
        from ecobank.sim import get_balance
        bal = get_balance(account_id)
        return jsonify({'account_id': account_id, 'balance': bal})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ecobank/simulate/<account_id>', methods=['POST'])
def ecobank_simulate(account_id):
    # Somente em modo simulate para evitar transações reais acidentais
    if str(os.environ.get('FIN_SIMULATE', '1')).lower() not in ('1', 'true', 'yes'):
        return jsonify({'error': 'FIN_SIMULATE disabled'}), 403
    try:
        from ecobank.sim import add_transaction
        # simulate_revenue no longer provided; perform a small add_transaction as demo
        amount = float(request.json.get('amount', 100.0)) if request.is_json else 100.0
        tx = add_transaction(account_id, amount, description='simulate_revenue')
        return jsonify(tx)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ecobank/transactions/<account_id>', methods=['GET'])
def ecobank_transactions(account_id):
    try:
        from ecobank.sim import list_transactions
        items = list_transactions()
        # filter by account
        filtered = [t for t in items if t.get('account_id') == account_id]
        return jsonify({'account_id': account_id, 'transactions': filtered})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/ecobank/transaction/<account_id>', methods=['POST'])
def ecobank_add_transaction(account_id):
    # Real financial ops require explicit approval token/flag to avoid accidents
    require_approval = str(os.environ.get('REQUIRE_FIN_APPROVAL', '1')).lower() in ('1', 'true', 'yes')
    data = request.get_json() or {}
    amount = float(data.get('amount'))
    description = data.get('description', '')

    if require_approval:
        # create a pending transaction to be approved by 2 admins
        try:
            from ecobank.pending import add_pending
            created_by = request.headers.get('X-ADMIN-ID') or request.args.get('admin_id')
            pending = add_pending(account_id, amount, description, created_by=created_by)
            return jsonify({'status': 'pending', 'pending': pending})
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    # no approval required -> execute immediately (use gateway or offline ledger)
    try:
        from ecobank.sim import add_transaction
        tx = add_transaction(account_id, amount, description)
        return jsonify(tx)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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


        @app.route('/admin/autonomy/start', methods=['POST'])
        def admin_autonomy_start():
            token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('admin_token')
            if not token or token != os.environ.get('ADMIN_DEPLOY_TOKEN'):
                abort(403)
            global _autonomy_thread, _autonomy_running
            if _autonomy_running:
                return jsonify({'status': 'already_running'})
            try:
                sys.path.append('..')
                from auto_evolution_loop import auto_evolution_loop

                def _runner():
                    try:
                        auto_evolution_loop()
                    except Exception as e:
                        print(f"[auto_evolution] erro no loop: {e}")

                _autonomy_thread = threading.Thread(target=_runner, daemon=True)
                _autonomy_thread.start()
                _autonomy_running = True
                return jsonify({'status': 'started'})
            except Exception as e:
                return jsonify({'error': str(e)}), 500


        @app.route('/admin/autonomy/stop', methods=['POST'])
        def admin_autonomy_stop():
            token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('admin_token')
            if not token or token != os.environ.get('ADMIN_DEPLOY_TOKEN'):
                abort(403)
            global _autonomy_thread, _autonomy_running
            # We cannot forcibly kill threads; use a cooperative flag file/stop signal.
            # Create a stop file that the loop should check (auto_evolution_loop should support this).
            stop_path = os.path.join(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')), 'autonomy_stop')
            try:
                with open(stop_path, 'w') as f:
                    f.write('stop')
            except Exception:
                pass
            _autonomy_running = False
            return jsonify({'status': 'stopping'})


            @app.route('/ecobank/pending', methods=['GET'])
            def ecobank_list_pending():
                token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('admin_token')
                if not token or token != os.environ.get('ADMIN_DEPLOY_TOKEN'):
                    abort(403)
                try:
                    from ecobank.pending import list_pending
                    return jsonify({'pending': list_pending()})
                except Exception as e:
                    return jsonify({'error': str(e)}), 500


            @app.route('/ecobank/pending/<pid>/approve', methods=['POST'])
            def ecobank_approve_pending(pid):
                # Approvals require admin tokens; two distinct admins needed
                approver_token = request.headers.get('X-ADMIN-TOKEN') or request.args.get('admin_token')
                approver_id = request.headers.get('X-ADMIN-ID') or request.args.get('admin_id')
                if not approver_token or not approver_id:
                    return jsonify({'error': 'approver token and approver id required'}), 403
                # Validate token matches one of the allowed admin tokens
                valid1 = os.environ.get('ADMIN_DEPLOY_TOKEN')
                valid2 = os.environ.get('ADMIN_DEPLOY_TOKEN_2')
                if approver_token not in (valid1, valid2):
                    return jsonify({'error': 'invalid approver token'}), 403
                try:
                    from ecobank.pending import approve_pending
                    res = approve_pending(pid, approver_token, approver_id)
                    return jsonify({'pending': res})
                except KeyError:
                    return jsonify({'error': 'pending_not_found'}), 404
                except Exception as e:
                    return jsonify({'error': str(e)}), 500
