from abc import ABC, abstractmethod
from typing import Any, Dict
import logging

logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for autonomous agents following the manifesto lifecycle."""

    def __init__(self, name: str):
        self.name = name

    def perceive(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Collect and normalize inputs/data."""
        logger.debug(f"{self.name}: perceiving context")
        return context

    @abstractmethod
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """Decide on actions to take."""

    @abstractmethod
    def act(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """Execute actions (safe by default)."""

    def evaluate(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Assess outcomes and return metrics/logs."""
        logger.debug(f"{self.name}: evaluating result")
        return {"ok": True, "result": result}

    def evolve(self, evaluation: Dict[str, Any]) -> None:
        """Optionally update internal state or code (placeholder)."""
        logger.debug(f"{self.name}: evolving with evaluation {evaluation}")

    def run_cycle(self, context: Dict[str, Any]) -> Dict[str, Any]:
        p = self.perceive(context)
        d = self.decide(p)
        r = self.act(d)
        e = self.evaluate(r)
        self.evolve(e)
        return {"perception": p, "decision": d, "result": r, "evaluation": e}
