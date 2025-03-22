# pifunc/adapters/websocket_adapter.py
import json
import asyncio
import threading
import inspect
from typing import Any, Callable, Dict, List, Set
import websockets
from websockets.server import WebSocketServerProtocol
from pifunc.adapters import ProtocolAdapter


class WebSocketAdapter(ProtocolAdapter):
    """Adapter protokołu WebSocket."""

    def __init__(self):
        self.functions = {}
        self.config = {}
        self.server = None
        self.server_task = None
        self.clients: Set[WebSocketServerProtocol] = set()
        self.namespaces = {}

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter WebSocket."""
        self.config = config

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako handler dla wydarzenia WebSocket."""
        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację WebSocket
        ws_config = metadata.get("websocket", {})
        event = ws_config.get("event", f"{func.__module__}.{service_name}")
        namespace = ws_config.get("namespace", "/")

        # Tworzymy namespace, jeśli nie istnieje
        if namespace not in self.namespaces:
            self.namespaces[namespace] = {}

        # Zapisujemy informacje o funkcji
        self.namespaces[namespace][event] = {
            "function": func,
            "metadata": metadata,
            "event": event
        }

    async def _handle_client(self, websocket: WebSocketServerProtocol, path: str):
        """Obsługuje połączenie klienta WebSocket."""
        # Dodajemy klienta do listy
        self.clients.add(websocket)

        try:
            # Pobieramy namespace dla ścieżki
            namespace = path
            if namespace not in self.namespaces:
                namespace = "/"

            # Pobieramy funkcje dla namespace
            namespace_functions = self.namespaces.get(namespace, {})

            if not namespace_functions:
                await websocket.send(json.dumps({
                    "error": f"Nieznany namespace: {namespace}"
                }))
                return

            # Informujemy klienta o dostępnych zdarzeniach
            available_events = list(namespace_functions.keys())
            await websocket.send(json.dumps({
                "type": "connection_established",
                "namespace": namespace,
                "available_events": available_events
            }))

            # Pętla obsługi wiadomości
            async for message in websocket:
                try:
                    # Parsujemy wiadomość JSON
                    data = json.loads(message)

                    # Pobieramy nazwę zdarzenia
                    event = data.get("event")
                    if not event:
                        await websocket.send(json.dumps({
                            "error": "Brak nazwy zdarzenia w wiadomości"
                        }))
                        continue

                    # Sprawdzamy, czy mamy zarejestrowaną funkcję dla tego zdarzenia
                    if event not in namespace_functions:
                        await websocket.send(json.dumps({
                            "error": f"Nieznane zdarzenie: {event}"
                        }))
                        continue

                    # Pobieramy funkcję
                    function_info = namespace_functions[event]
                    func = function_info["function"]

                    # Pobieramy dane wejściowe
                    kwargs = data.get("data", {})

                    # Wywołujemy funkcję
                    result = func(**kwargs)

                    # Obsługujemy coroutines
                    if asyncio.iscoroutine(result):
                        result = await result

                    # Wysyłamy odpowiedź
                    response = {
                        "event": f"{event}_response",
                        "result": result
                    }

                    await websocket.send(json.dumps(response))

                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        "error": "Nieprawidłowy format JSON"
                    }))
                except Exception as e:
                    await websocket.send(json.dumps({
                        "error": str(e)
                    }))
        except websockets.exceptions.ConnectionClosed:
            pass
        finally:
            # Usuwamy klienta z listy
            self.clients.remove(websocket)

    async def _serve_forever(self):
        """Uruchamia serwer WebSocket."""
        host = self.config.get("host", "0.0.0.0")
        port = self.config.get("port", 8081)

        # Tworzymy serwer
        async with websockets.serve(self._handle_client, host, port):
            print(f"Serwer WebSocket uruchomiony na ws://{host}:{port}")

            # Czekamy na zakończenie
            while True:
                await asyncio.sleep(3600)  # 1 godzina

    def _run_server(self):
        """Uruchamia pętlę zdarzeń asyncio w osobnym wątku."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Tworzymy i uruchamiamy zadanie serwera
        self.server_task = loop.create_task(self._serve_forever())

        try:
            loop.run_until_complete(self.server_task)
        except asyncio.CancelledError:
            pass
        finally:
            loop.close()

    def start(self) -> None:
        """Uruchamia serwer WebSocket."""
        # Uruchamiamy serwer w osobnym wątku
        self.server = threading.Thread(target=self._run_server)
        self.server.daemon = True
        self.server.start()

    def stop(self) -> None:
        """Zatrzymuje serwer WebSocket."""
        # Zamykamy wszystkie połączenia klientów
        if self.clients:
            for client in self.clients.copy():
                asyncio.run_coroutine_threadsafe(
                    client.close(),
                    client.loop
                )

        # Anulujemy zadanie serwera
        if self.server_task and not self.server_task.done():
            self.server_task.cancel()

        print("Serwer WebSocket zatrzymany")

    async def broadcast(self, namespace: str, event: str, data: Any):
        """Wysyła wiadomość do wszystkich klientów w danym namespace."""
        message = json.dumps({
            "event": event,
            "data": data
        })

        for client in self.clients:
            if client.path == namespace:
                try:
                    await client.send(message)
                except:
                    pass