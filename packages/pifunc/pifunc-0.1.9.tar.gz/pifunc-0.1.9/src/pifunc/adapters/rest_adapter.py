# pifunc/adapters/rest_adapter.py
import json
import inspect
import asyncio
import threading
import re
from typing import Any, Callable, Dict, List, Optional, Type, Tuple
import aiohttp
from aiohttp import web
from pifunc.adapters import ProtocolAdapter


class RESTAdapter(ProtocolAdapter):
    """Adapter protokołu REST (oparty na HTTP, ale z konwencjami RESTful)."""

    def __init__(self):
        self.config = {}
        self.routes = {}
        self.app = None
        self.runner = None
        self.site = None
        self.server_thread = None

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter REST."""
        self.config = config

        # Tworzymy aplikację aiohttp
        self.app = web.Application()

        # Konfigurujemy CORS, jeśli potrzebny
        if config.get("cors", False):
            import aiohttp_cors

            # Konfiguracja CORS
            cors = aiohttp_cors.setup(self.app, defaults={
                "*": aiohttp_cors.ResourceOptions(
                    allow_credentials=config.get("cors_credentials", True),
                    expose_headers=config.get("cors_expose_headers", "*"),
                    allow_headers=config.get("cors_allow_headers", "*"),
                    allow_methods=config.get("cors_allow_methods", ["*"])
                )
            })

            # Zapisujemy instancję CORS
            self.cors = cors
        else:
            self.cors = None

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako endpoint REST."""
        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację REST
        rest_config = metadata.get("rest", {})

        # Konfiguracja endpointu
        path = rest_config.get("path", f"/api/{func.__module__}/{service_name}")
        methods = rest_config.get("methods", ["GET", "POST"])

        # Konwersja pojedyńczej metody na listę
        if isinstance(methods, str):
            methods = [methods]

        # Sprawdzamy, czy ścieżka zawiera parametry (np. "/users/{id}")
        path_params = re.findall(r'{([^}]+)}', path)

        # Zapisujemy informacje o funkcji
        self.routes[path] = {
            "function": func,
            "metadata": metadata,
            "path": path,
            "methods": methods,
            "path_params": path_params
        }

    async def _handle_request(self, request):
        """Obsługuje żądanie HTTP."""
        # Pobieramy ścieżkę
        path = request.path
        method = request.method

        # Szukamy dopasowania ścieżki
        matched_route = None
        matched_params = {}

        # Najpierw próbujemy dokładne dopasowanie
        if path in self.routes:
            matched_route = self.routes[path]
        else:
            # Jeśli nie ma dokładnego dopasowania, próbujemy dopasować wzorzec
            for route_path, route_info in self.routes.items():
                # Jeśli ścieżka nie zawiera parametrów, pomijamy
                if not route_info["path_params"]:
                    continue

                # Konwertujemy ścieżkę na wyrażenie regularne
                pattern = route_path
                for param in route_info["path_params"]:
                    pattern = pattern.replace(f"{{{param}}}", f"(?P<{param}>[^/]+)")

                # Dodajemy ograniczniki na początek i koniec
                pattern = f"^{pattern}$"

                # Próbujemy dopasować
                match = re.match(pattern, path)
                if match:
                    matched_route = route_info
                    matched_params = match.groupdict()
                    break

        if not matched_route:
            return web.json_response(
                {"error": f"Endpoint not found: {path}"},
                status=404
            )

        # Sprawdzamy, czy metoda jest dopuszczalna
        if method not in matched_route["methods"]:
            return web.json_response(
                {"error": f"Method not allowed: {method}"},
                status=405
            )

        # Pobieramy funkcję
        func = matched_route["function"]

        try:
            # Pobieramy parametry
            kwargs = {}

            # Dodajemy parametry ze ścieżki
            kwargs.update(matched_params)

            # Pobieramy parametry z query string
            for name, value in request.query.items():
                kwargs[name] = value

            # Pobieramy parametry z body (JSON)
            if method in ["POST", "PUT", "PATCH"] and request.content_type == 'application/json':
                try:
                    body = await request.json()
                    if isinstance(body, dict):
                        kwargs.update(body)
                    else:
                        kwargs["body"] = body
                except json.JSONDecodeError:
                    return web.json_response(
                        {"error": "Invalid JSON body"},
                        status=400
                    )

            # Wykonujemy funkcję
            result = func(**kwargs)

            # Obsługujemy coroutines
            if asyncio.iscoroutine(result):
                result = await result

            # Zwracamy wynik
            return web.json_response({"result": result})

        except Exception as e:
            # Zwracamy informację o błędzie
            return web.json_response(
                {"error": str(e)},
                status=500
            )

    def _register_routes(self):
        """Rejestruje wszystkie trasy w aplikacji."""

        # Dodajemy obsługę zdrowia
        async def health_handler(request):
            return web.json_response({"status": "ok"})

        health_path = self.config.get("health_path", "/health")
        self.app.router.add_get(health_path, health_handler)

        # Dodajemy obsługę wszystkich tras
        for path, route_info in self.routes.items():
            # Tworzymy handler dla trasy
            handler = self._handle_request

            # Dodajemy trasę do aplikacji
            resource = self.app.router.add_resource(path)

            for method in route_info["methods"]:
                resource.add_route(method, handler)

            # Dodajemy CORS do trasy
            if self.cors:
                self.cors.add(resource)

    async def _run_server(self):
        """Uruchamia serwer REST."""
        host = self.config.get("host", "0.0.0.0")
        port = self.config.get("port", 8000)

        # Rejestrujemy trasy
        self._register_routes()

        # Uruchamiamy serwer
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, host, port)
        await self.site.start()

        print(f"Serwer REST uruchomiony na http://{host}:{port}")

        # Czekamy na zatrzymanie
        while True:
            await asyncio.sleep(3600)  # 1 godzina

    def _server_thread_func(self):
        """Funkcja wątku serwera."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._run_server())
            loop.run_forever()
        except Exception as e:
            print(f"Błąd serwera REST: {e}")
        finally:
            loop.close()

    def start(self) -> None:
        """Uruchamia adapter REST."""
        # Uruchamiamy serwer w osobnym wątku
        self.server_thread = threading.Thread(target=self._server_thread_func)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        """Zatrzymuje adapter REST."""
        # Zatrzymujemy serwer
        if self.site and self.runner:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self.site.stop())
                loop.run_until_complete(self.runner.cleanup())
            finally:
                loop.close()

        print("Serwer REST zatrzymany")