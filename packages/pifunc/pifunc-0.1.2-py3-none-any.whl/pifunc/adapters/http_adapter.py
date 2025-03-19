# pifunc/adapters/http_adapter.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import inspect
import json
from typing import Any, Callable, Dict, List
import asyncio
from pifunc.adapters import ProtocolAdapter


class HTTPAdapter(ProtocolAdapter):
    """Adapter protokołu HTTP wykorzystujący FastAPI."""

    def __init__(self):
        self.app = FastAPI(title="pifunc API")
        self.server = None
        self.config = {}

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter HTTP."""
        self.config = config

        # Włączamy CORS, jeśli jest potrzebny
        if config.get("cors", False):
            self.app.add_middleware(
                CORSMiddleware,
                allow_origins=config.get("cors_origins", ["*"]),
                allow_credentials=config.get("cors_credentials", True),
                allow_methods=config.get("cors_methods", ["*"]),
                allow_headers=config.get("cors_headers", ["*"]),
            )

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako endpoint HTTP."""
        # Pobieramy konfigurację HTTP
        http_config = metadata.get("http", {})
        if not http_config:
            # Jeśli nie ma konfiguracji, używamy domyślnych ustawień
            path = f"/api/{func.__module__}/{func.__name__}"
            method = "POST"
        else:
            path = http_config.get("path", f"/api/{func.__module__}/{func.__name__}")
            method = http_config.get("method", "POST")

        # Dynamicznie dodajemy endpoint
        async def endpoint(request: Request):
            try:
                # Pobieramy argumenty z body
                if method in ["POST", "PUT", "PATCH"]:
                    body = await request.json()
                    kwargs = body
                else:
                    # Dla GET, pobieramy argumenty z query params
                    kwargs = dict(request.query_params)

                # Wywołujemy funkcję
                result = func(**kwargs)

                # Jeśli funkcja zwraca coroutine, czekamy na wynik
                if asyncio.iscoroutine(result):
                    result = await result

                # Zwracamy wynik
                return {"result": result}

            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))

        # Dodajemy endpoint do FastAPI
        if method == "GET":
            self.app.get(path)(endpoint)
        elif method == "POST":
            self.app.post(path)(endpoint)
        elif method == "PUT":
            self.app.put(path)(endpoint)
        elif method == "DELETE":
            self.app.delete(path)(endpoint)
        elif method == "PATCH":
            self.app.patch(path)(endpoint)
        else:
            raise ValueError(f"Nieobsługiwana metoda HTTP: {method}")

    def start(self) -> None:
        """Uruchamia serwer HTTP."""
        port = self.config.get("port", 8080)
        host = self.config.get("host", "0.0.0.0")

        # Uruchamiamy serwer w osobnym wątku
        import threading
        def run_server():
            uvicorn.run(self.app, host=host, port=port)

        self.server = threading.Thread(target=run_server, daemon=True)
        self.server.start()

        print(f"Serwer HTTP uruchomiony na http://{host}:{port}")

    def stop(self) -> None:
        """Zatrzymuje serwer HTTP."""
        # FastAPI/Uvicorn nie ma prostej metody do zatrzymania serwera z zewnątrz
        # W rzeczywistej implementacji należałoby użyć bardziej zaawansowanej metody
        pass
