# pifunc/adapters/redis_adapter.py
import json
import asyncio
import threading
import time
import inspect
from typing import Any, Callable, Dict, List, Optional
import redis
from redis.client import PubSub
from pifunc.adapters import ProtocolAdapter


class RedisAdapter(ProtocolAdapter):
    """Adapter protokołu Redis Pub/Sub."""

    def __init__(self):
        self.client = None
        self.pubsub = None
        self.functions = {}
        self.config = {}
        self.listen_thread = None
        self.running = False

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter Redis."""
        self.config = config

        # Konfigurujemy klienta Redis
        host = config.get("host", "localhost")
        port = config.get("port", 6379)
        db = config.get("db", 0)
        password = config.get("password", None)
        socket_timeout = config.get("socket_timeout", 5)

        # Tworzymy klienta Redis
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            decode_responses=True  # Automatyczne dekodowanie odpowiedzi
        )

        # Tworzymy klienta PubSub
        self.pubsub = self.client.pubsub(ignore_subscribe_messages=True)

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako handler dla kanału Redis."""
        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację Redis
        redis_config = metadata.get("redis", {})
        channel = redis_config.get("channel", f"{func.__module__}:{service_name}")
        pattern = redis_config.get("pattern", False)

        # Zapisujemy informacje o funkcji
        self.functions[channel] = {
            "function": func,
            "metadata": metadata,
            "channel": channel,
            "pattern": pattern,
            "response_channel": f"{channel}:response"
        }

    def _message_handler(self, message):
        """Obsługuje wiadomości otrzymane przez PubSub."""
        if message["type"] not in ["message", "pmessage"]:
            return

        # Pobieramy kanał
        channel = message["channel"]
        if message["type"] == "pmessage":
            # Dla wzorców używamy oryginalnego wzorca
            pattern = message["pattern"]
            function_info = self.functions.get(pattern)
        else:
            # Dla zwykłych kanałów używamy dokładnego dopasowania
            function_info = self.functions.get(channel)

        if not function_info:
            print(f"Brak zarejestrowanej funkcji dla kanału: {channel}")
            return

        # Pobieramy dane wiadomości
        data = message["data"]

        try:
            # Parsujemy JSON
            kwargs = json.loads(data)

            # Wywołujemy funkcję
            func = function_info["function"]
            result = func(**kwargs)

            # Obsługujemy coroutines
            if asyncio.iscoroutine(result):
                # Tworzymy nową pętlę asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(result)
                loop.close()

            # Serializujemy wynik
            response = json.dumps({
                "result": result,
                "channel": channel,
                "timestamp": time.time()
            })

            # Publikujemy odpowiedź
            response_channel = function_info["response_channel"]
            self.client.publish(response_channel, response)

        except json.JSONDecodeError:
            print(f"Błąd parsowania JSON: {data}")
        except Exception as e:
            # Publikujemy błąd
            error_response = json.dumps({
                "error": str(e),
                "channel": channel,
                "timestamp": time.time()
            })
            error_channel = f"{channel}:error"
            self.client.publish(error_channel, error_response)
            print(f"Błąd podczas przetwarzania wiadomości: {e}")

    def _listen_for_messages(self):
        """Nasłuchuje wiadomości z Redis w osobnym wątku."""
        while self.running:
            try:
                # Nasłuchujemy wiadomości
                message = self.pubsub.get_message(timeout=1.0)
                if message:
                    self._message_handler(message)

                # Sprawdzamy, czy mamy nowe funkcje do zarejestrowania
                # i aktualizujemy subskrypcje
                self._update_subscriptions()

                time.sleep(0.01)  # Krótka przerwa dla CPU

            except redis.RedisError as e:
                print(f"Błąd Redis: {e}")
                time.sleep(1.0)  # Dłuższa przerwa w przypadku błędu
            except Exception as e:
                print(f"Nieoczekiwany błąd: {e}")
                time.sleep(1.0)

    def _update_subscriptions(self):
        """Aktualizuje subskrypcje Redis PubSub."""
        for channel, function_info in self.functions.items():
            if function_info.get("subscribed", False):
                continue

            # Subskrybujemy kanał lub wzorzec
            if function_info["pattern"]:
                self.pubsub.psubscribe(channel)
            else:
                self.pubsub.subscribe(channel)

            # Oznaczamy jako zasubskrybowane
            function_info["subscribed"] = True

    def start(self) -> None:
        """Uruchamia adapter Redis."""
        if self.running:
            return

        self.running = True

        # Aktualizujemy subskrypcje
        self._update_subscriptions()

        # Uruchamiamy wątek nasłuchujący
        self.listen_thread = threading.Thread(target=self._listen_for_messages)
        self.listen_thread.daemon = True
        self.listen_thread.start()

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 6379)
        print(f"Adapter Redis uruchomiony i połączony z {host}:{port}")

        # Publikujemy informację o uruchomieniu
        status_channel = self.config.get("status_channel", "pifunc:status")
        self.client.publish(
            status_channel,
            json.dumps({
                "status": "online",
                "timestamp": time.time(),
                "channels": list(self.functions.keys())
            })
        )

    def stop(self) -> None:
        """Zatrzymuje adapter Redis."""
        if not self.running:
            return

        self.running = False

        # Publikujemy informację o zatrzymaniu
        status_channel = self.config.get("status_channel", "pifunc:status")
        self.client.publish(
            status_channel,
            json.dumps({
                "status": "offline",
                "timestamp": time.time()
            })
        )

        # Odsubskrybujemy wszystkie kanały
        self.pubsub.unsubscribe()
        self.pubsub.punsubscribe()

        # Czekamy na zakończenie wątku
        if self.listen_thread and self.listen_thread.is_alive():
            self.listen_thread.join(timeout=2.0)

        # Zamykamy połączenia
        self.pubsub.close()
        self.client.close()

        print("Adapter Redis zatrzymany")