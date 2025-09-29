from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class AgentBase(ABC):
    """Classe base abstrata para agentes do sistema Nexo.

    Define a interface mínima que todos os agentes devem implementar:
    - `name`: nome do agente
    - `start()`/`stop()` (opcional)
    - `handle(input)` método principal para processar uma entrada
    - `to_dict()`/`from_dict()` para serialização mínima
    """

    name: str = "AgentBase"

    def __init__(self, **kwargs):
        # Guarda configurações/estado simples
        self.config = kwargs or {}

    def start(self) -> None:
        """Inicialização opcional do agente."""
        return None

    def stop(self) -> None:
        """Encerramento opcional do agente."""
        return None

    @abstractmethod
    def handle(self, payload: Any) -> Any:
        """Método principal que deve processar a entrada e retornar um resultado."""

    def to_dict(self) -> Dict[str, Any]:
        """Serializa o estado mínimo do agente."""
        return {"name": getattr(self, "name", self.__class__.__name__), "config": self.config}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentBase":
        """Cria uma instância simples a partir de dicionário; não reconstitui estado complexo."""
        return cls(**data.get("config", {}))
