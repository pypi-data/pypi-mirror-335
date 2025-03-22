# pifunc/adapters/__init__.py
from abc import ABC, abstractmethod
import inspect
import json
from typing import Any, Callable, Dict, List, Type


class ProtocolAdapter(ABC):
    """Bazowa klasa dla wszystkich adapterów protokołów."""

    @abstractmethod
    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter z podanymi ustawieniami."""
        pass

    @abstractmethod
    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję w adapterze protokołu."""
        pass

    @abstractmethod
    def start(self) -> None:
        """Uruchamia serwer dla danego protokołu."""
        pass

    @abstractmethod
    def stop(self) -> None:
        """Zatrzymuje serwer."""
        pass