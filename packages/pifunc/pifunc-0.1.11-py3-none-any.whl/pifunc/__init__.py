"""
pifunc - Generate directory structures from ASCII art or Markdown files.
"""

from .cli import main
from functools import wraps
# Import adapters
from .adapters.http_adapter import HTTPAdapter
from .adapters.websocket_adapter import WebSocketAdapter
from .adapters.grpc_adapter import GRPCAdapter
from .adapters.zeromq_adapter import ZeroMQAdapter
from .adapters.redis_adapter import RedisAdapter
from .adapters.mqtt_adapter import MQTTAdapter
from .adapters.graphql_adapter import GraphQLAdapter
from .adapters.amqp_adapter import AMQPAdapter
from .adapters.cron_adapter import CRONAdapter

import inspect
import sys
import os
import signal
import importlib.util
from typing import Any, Callable, Dict, List, Optional, Set, Type

__version__ = "0.1.8"
__all__ = ["service", "run_services", "load_module_from_file", "main", "http", "websocket", "grpc", "mqtt", "zeromq", "redis", "amqp", "graphql", "cron"]

# Rejestr wszystkich zarejestrowanych funkcji
_SERVICE_REGISTRY = {}
_CLIENT_REGISTRY = {}

def http(path, method="GET"):
    """HTTP route decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store HTTP configuration in function metadata
        wrapper._pifunc_http = {
            "path": path,
            "method": method
        }
        return wrapper

    return decorator

def websocket(event):
    """WebSocket event decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store WebSocket configuration in function metadata
        wrapper._pifunc_websocket = {
            "event": event
        }
        return wrapper

    return decorator

def grpc(service_name=None, method=None, streaming=False):
    """gRPC service decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store gRPC configuration in function metadata
        wrapper._pifunc_grpc = {
            "service_name": service_name or func.__name__,
            "method": method or func.__name__,
            "streaming": streaming
        }
        return wrapper

    return decorator

def mqtt(topic, qos=0):
    """MQTT topic decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store MQTT configuration in function metadata
        wrapper._pifunc_mqtt = {
            "topic": topic,
            "qos": qos
        }
        return wrapper

    return decorator

def zeromq(socket_type="REP", identity=None):
    """ZeroMQ socket decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store ZeroMQ configuration in function metadata
        wrapper._pifunc_zeromq = {
            "socket_type": socket_type,
            "identity": identity or func.__name__
        }
        return wrapper

    return decorator

def redis(channel=None, pattern=None, command=None):
    """Redis pub/sub or command decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store Redis configuration in function metadata
        wrapper._pifunc_redis = {
            "channel": channel,
            "pattern": pattern,
            "command": command or func.__name__
        }
        return wrapper

    return decorator

def amqp(queue=None, exchange=None, routing_key=None, exchange_type="direct"):
    """AMQP (RabbitMQ) decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store AMQP configuration in function metadata
        wrapper._pifunc_amqp = {
            "queue": queue or func.__name__,
            "exchange": exchange or "",
            "routing_key": routing_key or func.__name__,
            "exchange_type": exchange_type
        }
        return wrapper

    return decorator

def graphql(field_name=None, is_mutation=False, description=None):
    """GraphQL field decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store GraphQL configuration in function metadata
        wrapper._pifunc_graphql = {
            "field_name": field_name or func.__name__,
            "is_mutation": is_mutation,
            "description": description or func.__doc__ or ""
        }
        return wrapper

    return decorator

def cron(interval=None, at=None, cron_expression=None, description=None):
    """CRON job decorator."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Store CRON configuration in function metadata
        config = {}
        if interval:
            config["interval"] = interval
        if at:
            config["at"] = at
        if cron_expression:
            config["cron_expression"] = cron_expression
        if description:
            config["description"] = description or func.__doc__ or ""

        wrapper._pifunc_cron = config
        return wrapper

    return decorator

def client(
        protocol=None,
        service=None,
        **protocol_configs
):
    """
    Dekorator służący do rejestracji funkcji jako klienta usługi.

    Args:
        protocol: Protokół, przez który ma być wywołana usługa (http, grpc, zeromq, itd.).
        service: Nazwa usługi docelowej (domyślnie nazwa funkcji).
        **protocol_configs: Konfiguracje dla konkretnego protokołu.

    Returns:
        Dekorowana funkcja.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        # Ustalamy nazwę usługi docelowej
        target_service = service or func.__name__

        # Zbieramy metadane o funkcji klienckiej
        metadata = {
            "name": func.__name__,
            "target_service": target_service,
            "function": func,
            "module": func.__module__,
            "file": inspect.getfile(func),
            "_is_client_function": True
        }

        # Ustalamy protokół komunikacji
        if protocol:
            metadata["protocol"] = protocol
            # Dodajemy specyficzną konfigurację protokołu
            metadata[protocol] = protocol_configs

        # Rejestrujemy funkcję w rejestrze klientów
        _CLIENT_REGISTRY[func.__name__] = metadata

        # Ustawiamy atrybut _pifunc_client na dekorowanej funkcji
        wrapper._pifunc_client = metadata

        return wrapper

    return decorator

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
        available_protocols = ["grpc", "http", "mqtt", "websocket", "graphql", "zeromq", "redis", "amqp", "cron"]
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

        # Sprawdzamy, czy funkcja ma już skonfigurowane protokoły za pomocą dedykowanych dekoratorów
        if hasattr(func, '_pifunc_http'):
            metadata["http"] = func._pifunc_http

        if hasattr(func, '_pifunc_websocket'):
            metadata["websocket"] = func._pifunc_websocket

        if hasattr(func, '_pifunc_grpc'):
            metadata["grpc"] = func._pifunc_grpc

        if hasattr(func, '_pifunc_mqtt'):
            metadata["mqtt"] = func._pifunc_mqtt

        if hasattr(func, '_pifunc_zeromq'):
            metadata["zeromq"] = func._pifunc_zeromq

        if hasattr(func, '_pifunc_redis'):
            metadata["redis"] = func._pifunc_redis

        if hasattr(func, '_pifunc_amqp'):
            metadata["amqp"] = func._pifunc_amqp

        if hasattr(func, '_pifunc_graphql'):
            metadata["graphql"] = func._pifunc_graphql

        if hasattr(func, '_pifunc_cron'):
            metadata["cron"] = func._pifunc_cron

        # Dodajemy także konfigurację przekazaną jako argumenty dekoratora
        for protocol, config in protocol_configs.items():
            if protocol in available_protocols:
                metadata[protocol] = config

        # Sprawdzamy, czy funkcja jest klientem
        if hasattr(func, '_pifunc_client'):
            metadata["client"] = func._pifunc_client
            metadata["_is_client_function"] = True

        # Rejestrujemy funkcję w globalnym rejestrze
        _SERVICE_REGISTRY[service_name] = metadata

        # Ustawiamy atrybut _pifunc_service na dekorowanej funkcji
        wrapper._pifunc_service = metadata

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
    # Tworzymy słownik na adaptery
    adapters = {}
    clients = {}

    # Importujemy tylko te adaptery, które są potrzebne
    if "http" in config or "http" in _get_used_protocols():
        adapters["http"] = HTTPAdapter()

    if "websocket" in config or "websocket" in _get_used_protocols():
        adapters["websocket"] = WebSocketAdapter()

    if "grpc" in config or "grpc" in _get_used_protocols():
        adapters["grpc"] = GRPCAdapter()

    if "zeromq" in config or "zeromq" in _get_used_protocols():
        adapters["zeromq"] = ZeroMQAdapter()

    if "redis" in config or "redis" in _get_used_protocols():
        adapters["redis"] = RedisAdapter()

    if "mqtt" in config or "mqtt" in _get_used_protocols():
        adapters["mqtt"] = MQTTAdapter()

    if "graphql" in config or "graphql" in _get_used_protocols():
        adapters["graphql"] = GraphQLAdapter()

    if "amqp" in config or "amqp" in _get_used_protocols():
        adapters["amqp"] = AMQPAdapter()

    if "cron" in config or "cron" in _get_used_protocols():
        # Przygotowanie konfiguracji dla CRON, dodając dostępne klienty
        cron_config = config.get("cron", {}).copy() if "cron" in config else {}
        cron_config["clients"] = clients
        adapters["cron"] = CRONAdapter()
        config["cron"] = cron_config

    # Konfigurujemy adaptery
    for protocol, adapter in adapters.items():
        if protocol in config:
            adapter.setup(config[protocol])
        else:
            # Używamy domyślnej konfiguracji
            adapter.setup({})

    # Tworzymy klientów dla każdego protokołu
    from pifunc_client import PiFuncClient

    for protocol, adapter in adapters.items():
        # Tworzymy bazowy URL dla klienta w zależności od protokołu
        if protocol == "http":
            host = config.get("http", {}).get("host", "localhost")
            port = config.get("http", {}).get("port", 8080)
            base_url = f"http://{host}:{port}"
            clients[protocol] = PiFuncClient(base_url=base_url, protocol=protocol)

        elif protocol == "grpc":
            host = config.get("grpc", {}).get("host", "localhost")
            port = config.get("grpc", {}).get("port", 50051)
            base_url = f"{host}:{port}"
            clients[protocol] = PiFuncClient(base_url=base_url, protocol=protocol)

        elif protocol == "zeromq":
            host = config.get("zeromq", {}).get("host", "localhost")
            port = config.get("zeromq", {}).get("port", 5555)
            base_url = f"{host}:{port}"
            clients[protocol] = PiFuncClient(base_url=base_url, protocol=protocol)

        elif protocol == "amqp":
            host = config.get("amqp", {}).get("host", "localhost")
            port = config.get("amqp", {}).get("port", 5672)
            base_url = f"{host}:{port}"
            clients[protocol] = PiFuncClient(base_url=base_url, protocol=protocol)

        elif protocol == "graphql":
            host = config.get("graphql", {}).get("host", "localhost")
            port = config.get("graphql", {}).get("port", 8082)
            base_url = f"http://{host}:{port}/graphql"
            clients[protocol] = PiFuncClient(base_url=base_url, protocol=protocol)

    # Rejestrujemy funkcje w adapterach
    for service_name, metadata in _SERVICE_REGISTRY.items():
        enabled_protocols = metadata.get("protocols", [])

        for protocol in enabled_protocols:
            if protocol in adapters:
                adapters[protocol].register_function(metadata["function"], metadata)

    # Rejestrujemy funkcje klienckie w adapterze CRON
    if "cron" in adapters:
        # Aktualizujemy klientów w konfiguracji CRON
        adapters["cron"].config["clients"] = clients

        # Rejestrujemy funkcje klienckie
        for client_name, metadata in _CLIENT_REGISTRY.items():
            if "_is_client_function" in metadata:
                adapters["cron"].register_function(metadata["function"], metadata)

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