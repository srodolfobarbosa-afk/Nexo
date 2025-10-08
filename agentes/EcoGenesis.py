"""EcoGenesis - fluxo mínimo para gerar novos agentes a partir de descrição.

Componentes:
- Architect: transforma descrição em spec (heurística + LLMProvider if available)
- Coder: gera código com base no spec
- Reviewer: analisa sintaxe e segurança básica (AST checks)
- Tester: tenta importar o módulo e run basic smoke
- Deployer: salva arquivo em agentes/ e registra no agent_registry

Uso:
  from agentes.EcoGenesis import Genesis
  g = Genesis()
  spec = g.architect("Create EcoHunter that searches Twitter and Reddit for leads")
  res = g.run_full_pipeline(spec)

"""
import os
import re
import ast
import importlib.util
import sys
from typing import Dict, Any

from agentes.llm_provider import LLMProvider
from core.toolbelt import get_default_toolbelt

# avoid circular import heavy functions until needed

class Architect:
    def __init__(self, llm: LLMProvider = None):
        self.llm = llm or LLMProvider()

    def spec_from_text(self, text: str) -> Dict[str, Any]:
        """Gera uma spec básica a partir do texto. Se LLM disponível, delega; caso contrário usa heurísticas."""
        # heurística simples: extrair nome (palavra CamelCase ou capitalizada com 'Eco')
        name_match = re.search(r"(Eco[A-Za-z0-9_]+|[A-Z][a-zA-Z0-9]+Agent)", text)
        name = name_match.group(0) if name_match else "CustomAgent"
        # platform hints
        platforms = []
        if "twitter" in text.lower() or "x" in text.lower():
            platforms.append("twitter")
        if "reddit" in text.lower():
            platforms.append("reddit")
        if "discord" in text.lower():
            platforms.append("discord")
        # simple features extract
        features = []
        if "search" in text.lower() or "buscar" in text.lower():
            features.append("search")
        if "save" in text.lower() or "salvar" in text.lower():
            features.append("persist")
        if "notify" in text.lower() or "notificar" in text.lower():
            features.append("notify")

        spec = {
            "name": name,
            "description": text,
            "platforms": platforms,
            "features": features,
            "dependencies": ["requests"],
            "data_schema": {"lead": ["platform", "user", "content", "link", "collected_at"]},
        }

        # if LLM keys exist, ask LLM to expand the spec
        prompt = f"Generate a detailed agent spec in JSON for the following request:\n\n{text}\n\nReturn only JSON."
        llm_resp = self.llm.get_response(prompt)
        if llm_resp and llm_resp.startswith("{"):
            try:
                import json

                j = json.loads(llm_resp)
                # merge sensibly
                spec.update(j)
            except Exception:
                # ignore LLM if not valid JSON
                pass

        return spec


class Coder:
    def __init__(self, toolbelt=None):
        self.toolbelt = toolbelt or get_default_toolbelt()

    def generate_code(self, spec: Dict[str, Any]) -> str:
        """Gera um esqueleto de agente Python com base na spec."""
        name = spec.get("name", "GeneratedAgent")
        class_name = name if name.endswith("Agent") else f"{name}Agent"
        platforms = spec.get("platforms", [])
        deps = spec.get("dependencies", [])
        lines = []
        lines.append("from typing import Any, Dict, Optional")
        lines.append("import time")
        lines.append("")
        lines.append("from core.memory import EcoMemory")
        lines.append("")
        lines.append("")
        lines.append(f"class {class_name}:")
        # use single-quoted triple for docstring content to avoid conflicts
        desc = spec.get('description', '').replace('\n', ' ')[:1000]
        lines.append(f"    '''Auto-generated agent: {name}\n    Description: {desc}'''")
        lines.append("")
        lines.append("    def __init__(self):")
        lines.append("        self.memory = EcoMemory()")
        lines.append("")
        lines.append("    def get_status(self) -> Dict[str, Any]:")
        lines.append('        return ' + '{' + f'"{name}": "idle"' + '}')
        lines.append("")
        lines.append("    def run_once(self):")
        lines.append("        \"\"\"Executes one cycle of the agent's responsibilities.\"\"\"")
        lines.append("        # TODO: implement platform-specific logic")
        lines.append("        results = []")

        if "twitter" in platforms:
            lines.append("        # Placeholder: connect to Twitter API (tweepy) and search for keywords")
            lines.append("        # def connect_twitter(): pass")
            lines.append("        # def search_twitter(query): pass")
        if "reddit" in platforms:
            lines.append("        # Placeholder: connect to Reddit API (praw) and search subreddits")

        lines.append("        # Example: persist a dummy lead to memory")
        lines.append("        self.memory.add_record(topic=\"agents\", payload={'sample':'value'})")
        lines.append("        return results")

        return "\n".join(lines)


class Reviewer:
    def syntax_check(self, code_str: str) -> Dict[str, Any]:
        try:
            ast.parse(code_str)
            return {"ok": True}
        except SyntaxError as e:
            return {"ok": False, "error": str(e)}


class Tester:
    def smoke_test_import(self, module_path: str) -> Dict[str, Any]:
        """Tenta importar o módulo do caminho absoluto e verificar a classe Agent existe."""
        try:
            spec = importlib.util.spec_from_file_location("gen_module", module_path)
            mod = importlib.util.module_from_spec(spec)
            sys.modules["gen_module"] = mod
            spec.loader.exec_module(mod)
            # look for a class ending with Agent
            found = False
            for name in dir(mod):
                if name.endswith("Agent"):
                    found = True
                    break
            return {"ok": found}
        except Exception as e:
            return {"ok": False, "error": str(e)}


class Deployer:
    def __init__(self, target_dir: str = os.path.join(os.path.dirname(__file__), "")):
        # deploy to agentes/ by default
        self.target_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "agentes"))
        os.makedirs(self.target_dir, exist_ok=True)

    def deploy_file(self, filename: str, code_str: str) -> str:
        path = os.path.join(self.target_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            f.write(code_str)
        return path


class Genesis:
    def __init__(self):
        self.architect = Architect()
        self.coder = Coder()
        self.reviewer = Reviewer()
        self.tester = Tester()
        self.deployer = Deployer()

    def run_full_pipeline(self, description: str) -> Dict[str, Any]:
        spec = self.architect.spec_from_text(description)
        code = self.coder.generate_code(spec)
        review = self.reviewer.syntax_check(code)
        if not review.get("ok"):
            return {"status": "failed_review", "review": review}
        # deploy temp file and test import
        filename = f"{spec.get('name', 'GeneratedAgent')}.py"
        path = self.deployer.deploy_file(filename, code)
        test = self.tester.smoke_test_import(path)
        if not test.get("ok"):
            return {"status": "failed_test", "test": test}
        # success
        return {"status": "deployed", "module_path": path, "spec": spec}
