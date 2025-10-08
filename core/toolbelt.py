from typing import Callable, Dict, Any


class ToolRegistry:
    """Registry simples de ferramentas reutilizáveis (Toolbelt)."""

    def __init__(self):
        self._tools: Dict[str, Callable[..., Any]] = {}

    def register(self, name: str, func: Callable[..., Any]):
        self._tools[name] = func

    def call(self, name: str, *args, **kwargs):
        if name not in self._tools:
            raise KeyError(f"Tool '{name}' not registered")
        return self._tools[name](*args, **kwargs)


# exemplos de ferramentas leves
def eco_translate(text: str, target_lang: str = "pt") -> str:
    # placeholder: ideally usar um serviço de tradução
    return f"[traduzido para {target_lang}] {text}"


def eco_ping() -> str:
    return "pong"


# registrar ferramentas default
_default_registry = ToolRegistry()
_default_registry.register("translate", eco_translate)
_default_registry.register("ping", eco_ping)


def get_default_toolbelt() -> ToolRegistry:
    return _default_registry
