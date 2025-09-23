import os
import subprocess
import sys
import tempfile
import venv
import shutil
from datetime import datetime


def run_tests_in_sandbox(target_path: str = '.', python_exe: str = sys.executable) -> dict:
    """Cria um virtualenv temporário, instala pytest e executa os testes do target_path.

    Retorna dict com keys: success (bool), log_path (str), returncode (int).
    """
    ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    logs_dir = os.path.join(os.getcwd(), 'construction_logs')
    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f'test_run_{ts}.log')

    tmpdir = tempfile.mkdtemp(prefix='nexo_sandbox_')
    try:
        venv_dir = os.path.join(tmpdir, 'venv')
        venv.create(venv_dir, with_pip=True)
        py = os.path.join(venv_dir, 'bin', 'python')
        pip = os.path.join(venv_dir, 'bin', 'pip')

        # Instala pytest apenas
        subprocess.check_call([py, '-m', 'pip', 'install', '--upgrade', 'pip'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        subprocess.check_call([py, '-m', 'pip', 'install', 'pytest'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Executa pytest
        with open(log_path, 'w', encoding='utf-8') as f:
            proc = subprocess.Popen([py, '-m', 'pytest', '-q', target_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, cwd=os.getcwd())
            out, _ = proc.communicate()
            if out:
                f.write(out.decode('utf-8', errors='replace'))

        success = proc.returncode == 0
        return {"success": success, "log_path": log_path, "returncode": proc.returncode}
    except Exception as e:
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(f"Exception durante sandbox run: {e}\n")
        return {"success": False, "log_path": log_path, "returncode": -1}
    finally:
        try:
            shutil.rmtree(tmpdir)
        except Exception:
            pass


if __name__ == '__main__':
    res = run_tests_in_sandbox('.')
    print(res)
