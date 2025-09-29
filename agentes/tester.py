from core.agent_base import AgentBase
import tempfile
import subprocess
from pathlib import Path
import textwrap


class TesterAI(AgentBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Tester'

    def handle(self, payload: dict) -> dict:
        """Recebe payload com 'code' (str) e opcional 'test_code' (str).

        Escreve arquivos numa tempdir e executa pytest (se houver test code) ou executa o module.
        Retorna resultado com saída capturada.
        """
        code = payload.get('code', '')
        test_code = payload.get('test_code')
        if not code:
            return {"agent": self.name, "ok": False, "error": "no_code"}

        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            module_file = td_path / 'module_under_test.py'
            module_file.write_text(textwrap.dedent(code))

            if test_code:
                test_file = td_path / 'test_generated.py'
                test_file.write_text(textwrap.dedent(test_code))
                # run pytest in tempdir
                try:
                    res = subprocess.run(['pytest', '-q', str(test_file)], cwd=str(td_path), capture_output=True, text=True, timeout=20)
                    ok = res.returncode == 0
                    return {"agent": self.name, "ok": ok, "returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
                except Exception as e:
                    return {"agent": self.name, "ok": False, "error": str(e)}
            else:
                # execute module as script
                try:
                    res = subprocess.run(['python3', str(module_file)], cwd=str(td_path), capture_output=True, text=True, timeout=10)
                    ok = res.returncode == 0
                    return {"agent": self.name, "ok": ok, "returncode": res.returncode, "stdout": res.stdout, "stderr": res.stderr}
                except Exception as e:
                    return {"agent": self.name, "ok": False, "error": str(e)}
