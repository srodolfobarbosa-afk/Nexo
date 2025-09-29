from core.agent_base import AgentBase
import ast


class Reviewer(AgentBase):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.name = 'Reviewer'

    def _basic_sanity_checks(self, code: str) -> dict:
        issues = []
        try:
            tree = ast.parse(code)
        except Exception as e:
            return {"ok": False, "issues": [f"syntax_error: {e}"]}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name in ('os', 'subprocess'):
                        issues.append(f'dangerous_import: {alias.name}')
            if isinstance(node, ast.ImportFrom):
                mod = node.module or ''
                if mod.split('.')[0] in ('os', 'subprocess'):
                    issues.append(f'dangerous_import_from: {mod}')

        return {"ok": len(issues) == 0, "issues": issues}

    def handle(self, payload: dict) -> dict:
        code = payload.get('code', '')
        if not code:
            return {"agent": self.name, "ok": False, "issues": ['no_code_provided']}

        checks = self._basic_sanity_checks(code)
        if not checks.get('ok'):
            return {"agent": self.name, "ok": False, "issues": checks.get('issues', [])}

        return {"agent": self.name, "ok": True, "issues": [], "suggestion": 'Considere adicionar logging e tratamento de exceções.'}
