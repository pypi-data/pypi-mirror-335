# pifunc/adapters/mqtt_adapter.py
import paho.mqtt.client as mqtt
import json
import inspect
from typing import Any, Callable, Dict
import asyncio
import threading
from pifunc.adapters import ProtocolAdapter
import logging

logger = logging.getLogger(__name__)

class MQTTAdapter(ProtocolAdapter):
    """Adapter protokołu MQTT."""

    def __init__(self):
        self.client = mqtt.Client()
        self.functions = {}
        self.config = {}
        self._started = False

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

        try:
            # Łączymy się z brokerem
            self.client.connect(broker, port, 60)
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            raise

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
            "qos": qos,
            "signature": inspect.signature(func)
        }

    def _on_connect(self, client, userdata, flags, rc):
        """Callback wywoływany po połączeniu z brokerem."""
        if rc == 0:
            logger.info("Connected to MQTT broker")
            # Subskrybujemy wszystkie zarejestrowane tematy
            for topic, config in self.functions.items():
                try:
                    result, mid = client.subscribe(topic, config["qos"])
                    if result != mqtt.MQTT_ERR_SUCCESS:
                        logger.error(f"Failed to subscribe to topic {topic}: {result}")
                except Exception as e:
                    logger.error(f"Error subscribing to topic {topic}: {e}")
        else:
            logger.error(f"Failed to connect to MQTT broker with code {rc}")

    def _on_message(self, client, userdata, msg):
        """Callback wywoływany po otrzymaniu wiadomości."""
        topic = msg.topic
        logger.debug(f"Received message on topic {topic}")

        # Sprawdzamy, czy mamy zarejestrowaną funkcję dla tego tematu
        if topic in self.functions:
            func_config = self.functions[topic]
            func = func_config["function"]
            signature = func_config["signature"]

            try:
                # Dekodujemy wiadomość jako JSON
                try:
                    payload = json.loads(msg.payload.decode())
                    logger.debug(f"Decoded payload: {payload}")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to decode JSON payload: {e}")
                    self._publish_error(topic, f"Invalid JSON payload: {str(e)}")
                    return

                # Sprawdzamy i konwertujemy typy argumentów
                converted_kwargs = {}
                for param_name, param in signature.parameters.items():
                    if param_name in payload:
                        try:
                            if param.annotation == dict:
                                # For dict type, just pass through
                                converted_kwargs[param_name] = payload[param_name]
                            elif param.annotation != inspect.Parameter.empty:
                                converted_kwargs[param_name] = param.annotation(payload[param_name])
                            else:
                                converted_kwargs[param_name] = payload[param_name]
                        except (ValueError, TypeError) as e:
                            logger.error(f"Type conversion error for {param_name}: {e}")
                            self._publish_error(topic, f"Invalid type for parameter {param_name}: {str(e)}")
                            return

                # Wywołujemy funkcję
                try:
                    logger.debug(f"Calling function with kwargs: {converted_kwargs}")
                    result = func(**converted_kwargs)
                except TypeError as e:
                    logger.error(f"Function call error: {e}")
                    self._publish_error(topic, f"Invalid parameters: {str(e)}")
                    return
                except Exception as e:
                    logger.error(f"Function execution error: {e}")
                    self._publish_error(topic, f"Internal error: {str(e)}")
                    return

                # Jeśli funkcja zwraca coroutine, uruchamiamy je w pętli asyncio
                if asyncio.iscoroutine(result):
                    try:
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        result = loop.run_until_complete(result)
                        loop.close()
                    except Exception as e:
                        logger.error(f"Async execution error: {e}")
                        self._publish_error(topic, f"Async execution error: {str(e)}")
                        return

                # Publikujemy wynik
                response_topic = f"{topic}/response"
                try:
                    response_payload = json.dumps({"result": result})
                    logger.debug(f"Publishing response to {response_topic}: {response_payload}")
                    self.client.publish(response_topic, response_payload)
                except Exception as e:
                    logger.error(f"Failed to publish response: {e}")

            except Exception as e:
                logger.error(f"Unexpected error processing message: {e}")
                self._publish_error(topic, f"Unexpected error: {str(e)}")

    def _publish_error(self, topic: str, error_message: str) -> None:
        """Publikuje komunikat o błędzie."""
        error_topic = f"{topic}/error"
        try:
            error_payload = json.dumps({"error": error_message})
            logger.debug(f"Publishing error to {error_topic}: {error_message}")
            self.client.publish(error_topic, error_payload)
        except Exception as e:
            logger.error(f"Failed to publish error message: {e}")

    def start(self) -> None:
        """Uruchamia klienta MQTT."""
        if self._started:
            return

        try:
            # Uruchamiamy pętlę klienta w osobnym wątku
            self.client.loop_start()
            self._started = True

            broker = self.config.get("broker", "localhost")
            port = self.config.get("port", 1883)
            logger.info(f"MQTT client started and connected to {broker}:{port}")
            print(f"Klient MQTT uruchomiony i połączony z {broker}:{port}")
        except Exception as e:
            logger.error(f"Failed to start MQTT client: {e}")
            raise

    def stop(self) -> None:
        """Zatrzymuje klienta MQTT."""
        if not self._started:
            return

        try:
            self.client.loop_stop()
            self.client.disconnect()
            self._started = False
            logger.info("MQTT client stopped")
        except Exception as e:
            logger.error(f"Error stopping MQTT client: {e}")
