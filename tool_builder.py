import os
import importlib.util

class ToolBuilder:
    def __init__(self, tools_dir='ferramentas'):
        self.tools_dir = tools_dir
        os.makedirs(self.tools_dir, exist_ok=True)
        self.registry_path = os.path.join(self.tools_dir, 'tool_registry.json')
        self._init_registry()

    def _init_registry(self):
        if not os.path.exists(self.registry_path):
            with open(self.registry_path, 'w') as f:
                f.write('{}')

    def create_tool(self, name, code):
        """
        Cria uma ferramenta Python sob demanda.
        name: nome da ferramenta (ex: 'validador_url')
        code: string com código Python da função ou classe
        """
        tool_path = os.path.join(self.tools_dir, f'{name}.py')
        with open(tool_path, 'w') as f:
            f.write(code)
        self._register_tool(name, tool_path)
        return tool_path

    def _register_tool(self, name, path):
        import json
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        registry[name] = path
        with open(self.registry_path, 'w') as f:
            json.dump(registry, f)

    def load_tool(self, name):
        import json
        with open(self.registry_path, 'r') as f:
            registry = json.load(f)
        path = registry.get(name)
        if not path or not os.path.exists(path):
            raise ImportError(f"Ferramenta '{name}' não encontrada.")
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

# Exemplo de uso:
if __name__ == "__main__":
    tb = ToolBuilder()
    code = """
def validar_url(url):
    import re
    return bool(re.match(r'^https?://', url))
"""
    tb.create_tool('validador_url', code)
    mod = tb.load_tool('validador_url')
    print(mod.validar_url('https://nexo.ai'))
