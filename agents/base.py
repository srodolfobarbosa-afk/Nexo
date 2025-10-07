from abc import ABC, abstractmethod
from typing import Any, Dict


class StorageInterface(ABC):
    @abstractmethod
    def save_action(self, action: Dict[str, Any]) -> None:
        raise NotImplementedError()


class Agent(ABC):
    def __init__(self, config: Dict[str, Any], storage: StorageInterface | None = None):
        self.config = config
        self.storage = storage

    @abstractmethod
    def decide(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Return an action dict based on context."""
        raise NotImplementedError()

    def run_once(self, context: Dict[str, Any]) -> Dict[str, Any]:
        action = self.decide(context)
        if self.storage:
            try:
                self.storage.save_action(action)
            except Exception:
                # storage errors should not break agent logic
                pass
        return action

    def run_continuous(self, context_supplier, interval: int = 5):
        """Run agent continuously calling context_supplier() every interval seconds.

        This method is a convenience; in production use a worker/scheduler.
        """
        import time

        while True:
            ctx = context_supplier()
            self.run_once(ctx)
            time.sleep(interval)
