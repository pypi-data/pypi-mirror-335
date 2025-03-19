"""
pifunc - Generate directory structures from ASCII art or Markdown files.
"""

# from .generator import DirectoryStructureGenerator
# from .cli import main

__version__ = "0.1.0"
__all__ = ["service", "run_services", "load_module_from_file"]

# pifunc/__init__.py
import inspect
import sys
import os
import signal
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Set, Type
from functools import wraps

# Rejestr wszystkich zarejestrowanych funkcji
_SERVICE_REGISTRY = {}


def service(
        protocols: Optional[List[str]] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        **protocol_configs
):
    """
    Dekorator służący do rejestracji funkcji jako usługi dostępnej przez różne protokoły.

    Args:
        protocols: Lista protokołów, przez które funkcja ma być dostępna.
                  Domyślnie włączone są wszystkie obsługiwane protokoły.
        name: Nazwa usługi (domyślnie nazwa funkcji).
        description: Opis usługi (domyślnie docstring funkcji).
        **protocol_configs: Konfiguracje dla poszczególnych protokołów.
                           Np. http={"path": "/api/add", "method": "POST"}

    Returns:
        Dekorowana funkcja.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Ustalamy nazwę i opis
        service_name = name or func.__name__
        service_description = description or func.__doc__ or ""

        # Ustalamy protokoły
        available_protocols = ["grpc", "http", "mqtt", "websocket", "graphql"]
        enabled_protocols = protocols or available_protocols

        # Analizujemy sygnaturę funkcji
        signature = inspect.signature(func)

        # Zbieramy metadane o funkcji
        metadata = {
            "name": service_name,
            "description": service_description,
            "function": func,
            "module": func.__module__,
            "file": inspect.getfile(func),
            "signature": {
                "parameters": {},
                "return_annotation": None
            },
            "protocols": enabled_protocols
        }

        # Dodajemy informacje o parametrach
        for param_name, param in signature.parameters.items():
            metadata["signature"]["parameters"][param_name] = {
                "annotation": param.annotation if param.annotation != inspect.Parameter.empty else None,
                "default": None if param.default == inspect.Parameter.empty else param.default
            }

        # Dodajemy informację o typie zwracanym
        metadata["signature"][
            "return_annotation"] = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None

        # Dodajemy konfiguracje dla poszczególnych protokołów
        for protocol, config in protocol_configs.items():
            if protocol in available_protocols:
                metadata[protocol] = config

        # Rejestrujemy funkcję w globalnym rejestrze
        _SERVICE_REGISTRY[service_name] = metadata

        return wrapper

    # Obsługa przypadku, gdy dekorator jest użyty bez nawiasów
    if callable(protocols):
        func = protocols
        protocols = None
        return decorator(func)

    return decorator


def run_services(**config):
    """
    Uruchamia wszystkie zarejestrowane usługi z podaną konfiguracją.

    Args:
        **config: Konfiguracja dla poszczególnych protokołów i ogólne ustawienia.
                 Np. grpc={"port": 50051}, http={"port": 8080}, watch=True
    """
    # Importujemy adaptery protokołów
    from pifunc.adapters.http_adapter import HTTPAdapter
    from pifunc.adapters.mqtt_adapter import MQTTAdapter
    from pifunc.adapters.grpc_adapter import GRPCAdapter
    from pifunc.adapters.websocket_adapter import WebSocketAdapter
    from pifunc.adapters.graphql_adapter import GraphQLAdapter

    # Tworzymy adaptery dla wszystkich obsługiwanych protokołów
    adapters = {
        "grpc": GRPCAdapter(),
        "http": HTTPAdapter(),
        "mqtt": MQTTAdapter(),
        "websocket": WebSocketAdapter(),
        "graphql": GraphQLAdapter()
    }

    # Konfigurujemy adaptery
    for protocol, adapter in adapters.items():
        if protocol in config:
            adapter.setup(config[protocol])
        else:
            # Używamy domyślnej konfiguracji
            adapter.setup({})

    # Rejestrujemy funkcje w adapterach
    for service_name, metadata in _SERVICE_REGISTRY.items():
        enabled_protocols = metadata.get("protocols", [])

        for protocol in enabled_protocols:
            if protocol in adapters:
                adapters[protocol].register_function(metadata["function"], metadata)

    # Uruchamiamy adaptery
    for protocol, adapter in adapters.items():
        if protocol in config or protocol in _get_used_protocols():
            adapter.start()

    # Jeśli włączone jest watchowanie, uruchamiamy wątek monitorujący
    if config.get("watch", False):
        _start_file_watcher(adapters)

    # Konfigurujemy handler dla sygnałów, aby graceful shutdown
    def handle_signal(signum, frame):
        print("Zatrzymywanie serwerów...")
        for adapter in adapters.values():
            adapter.stop()
        sys.exit(0)

    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)

    print(f"Uruchomiono {len(_SERVICE_REGISTRY)} usług przez {len(_get_used_protocols())} protokołów.")

    # Blokujemy główny wątek
    try:
        while True:
            # Używamy signal.pause() zamiast sleep, aby lepiej reagować na sygnały
            if hasattr(signal, 'pause'):
                signal.pause()
            else:
                # W systemach, które nie obsługują signal.pause()
                import time
                time.sleep(3600)
    except KeyboardInterrupt:
        handle_signal(None, None)


def _get_used_protocols() -> Set[str]:
    """Zwraca zbiór protokołów używanych przez zarejestrowane usługi."""
    used_protocols = set()

    for metadata in _SERVICE_REGISTRY.values():
        used_protocols.update(metadata.get("protocols", []))

    return used_protocols


def _start_file_watcher(adapters):
    """Uruchamia wątek monitorujący zmiany w plikach."""
    import threading
    import time

    def watch_files():
        file_times = {}

        # Zbieramy pliki, w których zdefiniowane są usługi
        for metadata in _SERVICE_REGISTRY.values():
            file_path = metadata.get("file")
            if file_path and os.path.exists(file_path):
                file_times[file_path] = os.path.getmtime(file_path)

        while True:
            # Sprawdzamy, czy któryś plik został zmodyfikowany
            changed = False
            for file_path in list(file_times.keys()):
                try:
                    mtime = os.path.getmtime(file_path)

                    # Jeśli plik został zmodyfikowany
                    if file_times[file_path] < mtime:
                        print(f"Plik {file_path} został zmodyfikowany. Przeładowywanie...")
                        file_times[file_path] = mtime
                        changed = True
                except:
                    pass

            # Jeśli jakiś plik został zmodyfikowany, przeładowujemy serwery
            if changed:
                # Zatrzymujemy wszystkie adaptery
                for adapter in adapters.values():
                    adapter.stop()

                # Restartujemy proces
                os.execv(sys.executable, [sys.executable] + sys.argv)

            time.sleep(1)

    thread = threading.Thread(target=watch_files, daemon=True)
    thread.start()


# Funkcja do załadowania modułu z pliku
def load_module_from_file(file_path):
    """Ładuje moduł z pliku."""
    module_name = os.path.basename(file_path).replace('.py', '')
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module