# pifunc/adapters/mqtt_adapter.py
import paho.mqtt.client as mqtt
import json
import inspect
from typing import Any, Callable, Dict
import asyncio
import threading
from pifunc.adapters import ProtocolAdapter


class MQTTAdapter(ProtocolAdapter):
    """Adapter protokołu MQTT."""

    def __init__(self):
        self.client = mqtt.Client()
        self.functions = {}
        self.config = {}

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter MQTT."""
        self.config = config

        # Konfigurujemy klienta MQTT
        broker = config.get("broker", "localhost")
        port = config.get("port", 1883)
        username = config.get("username", None)
        password = config.get("password", None)

        if username and password:
            self.client.username_pw_set(username, password)

        # Ustawiamy callbacki
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message

        # Łączymy się z brokerem
        self.client.connect(broker, port, 60)

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako handler dla tematu MQTT."""
        # Pobieramy konfigurację MQTT
        mqtt_config = metadata.get("mqtt", {})
        if not mqtt_config:
            # Jeśli nie ma konfiguracji, używamy domyślnych ustawień
            topic = f"{func.__module__}/{func.__name__}"
            qos = 0
        else:
            topic = mqtt_config.get("topic", f"{func.__module__}/{func.__name__}")
            qos = mqtt_config.get("qos", 0)

        # Zapisujemy funkcję wraz z konfiguracją
        self.functions[topic] = {
            "function": func,
            "qos": qos
        }

    def _on_connect(self, client, userdata, flags, rc):
        """Callback wywoływany po połączeniu z brokerem."""
        print(f"Połączono z brokerem MQTT z kodem {rc}")

        # Subskrybujemy wszystkie zarejestrowane tematy
        for topic, config in self.functions.items():
            client.subscribe(topic, config["qos"])

    def _on_message(self, client, userdata, msg):
        """Callback wywoływany po otrzymaniu wiadomości."""
        topic = msg.topic

        # Sprawdzamy, czy mamy zarejestrowaną funkcję dla tego tematu
        if topic in self.functions:
            func_config = self.functions[topic]
            func = func_config["function"]

            try:
                # Dekodujemy wiadomość jako JSON
                payload = json.loads(msg.payload.decode())

                # Wywołujemy funkcję
                result = func(**payload)

                # Jeśli funkcja zwraca coroutine, uruchamiamy je w pętli asyncio
                if asyncio.iscoroutine(result):
                    # Tworzymy nową pętlę asyncio
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(result)
                    loop.close()

                # Publikujemy wynik
                response_topic = f"{topic}/response"
                self.client.publish(response_topic, json.dumps({"result": result}))

            except Exception as e:
                # Publikujemy błąd
                error_topic = f"{topic}/error"
                self.client.publish(error_topic, json.dumps({"error": str(e)}))

    def start(self) -> None:
        """Uruchamia klienta MQTT."""
        # Uruchamiamy pętlę klienta w osobnym wątku
        self.client.loop_start()

        broker = self.config.get("broker", "localhost")
        port = self.config.get("port", 1883)
        print(f"Klient MQTT uruchomiony i połączony z {broker}:{port}")

    def stop(self) -> None:
        """Zatrzymuje klienta MQTT."""
        self.client.loop_stop()
        self.client.disconnect()
