# pifunc/adapters/http_adapter.py
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import inspect
import json
from typing import Any, Callable, Dict, List
import asyncio
from pifunc.adapters import ProtocolAdapter
import threading
import socket
import time
import logging

logger = logging.getLogger(__name__)

class UvicornServer(uvicorn.Server):
    """Uvicorn server that can be started and stopped."""
    
    def install_signal_handlers(self):
        """Override to disable signal handlers that interfere with testing."""
        pass


class HTTPAdapter(ProtocolAdapter):
    """Adapter protokołu HTTP wykorzystujący FastAPI."""

    def __init__(self):
        self.app = FastAPI(title="pifunc API")
        self.server = None
        self.config = {}
        self._started = False
        self._server_thread = None

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
                kwargs = {}
                # Pobieramy argumenty z body dla POST/PUT/PATCH
                if method in ["POST", "PUT", "PATCH"]:
                    try:
                        body = await request.json()
                        logger.debug(f"Received request body: {body}")
                        kwargs = body
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decode error: {e}")
                        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")

                # Dla GET, pobieramy argumenty z path params i query params
                else:
                    # Combine path params and query params
                    kwargs.update(request.path_params)
                    kwargs.update(request.query_params)

                # Convert types if needed
                sig = inspect.signature(func)
                logger.debug(f"Function signature: {sig}")
                logger.debug(f"Received kwargs: {kwargs}")

                converted_kwargs = {}
                for param_name, param in sig.parameters.items():
                    if param_name in kwargs:
                        try:
                            if param.annotation == dict:
                                # For dict type, just pass through
                                converted_kwargs[param_name] = kwargs[param_name]
                            elif param.annotation != inspect.Parameter.empty:
                                converted_kwargs[param_name] = param.annotation(kwargs[param_name])
                            else:
                                converted_kwargs[param_name] = kwargs[param_name]
                        except (ValueError, TypeError) as e:
                            logger.error(f"Type conversion error for {param_name}: {e}")
                            raise HTTPException(
                                status_code=400,
                                detail=f"Invalid type for parameter {param_name}: {str(e)}"
                            )

                # Wywołujemy funkcję
                try:
                    logger.debug(f"Calling function with kwargs: {converted_kwargs}")
                    result = func(**converted_kwargs)
                except TypeError as e:
                    logger.error(f"Function call error: {e}")
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid parameters: {str(e)}"
                    )
                except Exception as e:
                    logger.error(f"Function execution error: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail=f"Internal error: {str(e)}"
                    )

                # Jeśli funkcja zwraca coroutine, czekamy na wynik
                if asyncio.iscoroutine(result):
                    try:
                        result = await result
                    except Exception as e:
                        logger.error(f"Async execution error: {e}")
                        raise HTTPException(
                            status_code=500,
                            detail=f"Async execution error: {str(e)}"
                        )

                # Zwracamy wynik
                return {"result": result}

            except HTTPException:
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
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
        if self._started:
            return

        port = self.config.get("port", 8080)
        host = self.config.get("host", "0.0.0.0")

        config = uvicorn.Config(
            app=self.app,
            host=host,
            port=port,
            log_level="error"
        )
        self.server = UvicornServer(config=config)

        def run_server():
            asyncio.run(self.server.serve())

        self._server_thread = threading.Thread(target=run_server, daemon=True)
        self._server_thread.start()

        # Wait for server to start
        for _ in range(10):  # Try for 1 second
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.connect((host, port))
                self._started = True
                print(f"Serwer HTTP uruchomiony na http://{host}:{port}")
                return
            except (ConnectionRefusedError, socket.error):
                time.sleep(0.1)
        
        raise RuntimeError("Failed to start HTTP server")

    def stop(self) -> None:
        """Zatrzymuje serwer HTTP."""
        if not self._started:
            return

        if self.server:
            self.server.should_exit = True
            if self._server_thread:
                self._server_thread.join(timeout=1.0)
            self._started = False
