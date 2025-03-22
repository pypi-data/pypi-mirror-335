# pifunc/adapters/amqp_adapter.py
import json
import asyncio
import threading
import time
import inspect
from typing import Any, Callable, Dict, List, Optional
import pika
from pika.exchange_type import ExchangeType
from pifunc.adapters import ProtocolAdapter
import logging

logger = logging.getLogger(__name__)


class AMQPAdapter(ProtocolAdapter):
    """Adapter protokołu AMQP (RabbitMQ)."""

    def __init__(self):
        self.connection = None
        self.channel = None
        self.functions = {}
        self.config = {}
        self.consuming = False
        self.consumer_thread = None
        self._connected = False

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter AMQP."""
        self.config = config

        # Konfiguracja połączenia
        host = config.get("host", "localhost")
        port = config.get("port", 5672)
        virtual_host = config.get("virtual_host", "/")
        username = config.get("username", "guest")
        password = config.get("password", "guest")
        # Dodajemy flagę wymuszania połączenia
        self.force_connection = config.get("force_connection", False)

        # Tworzymy parametry połączenia
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials,
            heartbeat=60
        )

        try:
            # Tworzymy połączenie tylko jeśli wymuszono połączenie
            if self.force_connection:
                self.connection = pika.BlockingConnection(parameters)
                self._connected = True
            else:
                # Próbujemy się połączyć, ale ignorujemy błędy
                try:
                    self.connection = pika.BlockingConnection(parameters)
                    self._connected = True
                except Exception as e:
                    logger.warning(f"Failed to connect to AMQP broker: {e}")
                    print(f"Warning: AMQP broker not available at {host}:{port}")
                    print("AMQP features will be disabled. Set force_connection=True to require AMQP connection.")
                    self._connected = False
                    return
        except Exception as e:
            if self.force_connection:
                logger.error(f"Failed to connect to AMQP broker: {e}")
                raise
            else:
                logger.warning(f"Failed to connect to AMQP broker: {e}")
                print(f"Warning: AMQP broker not available at {host}:{port}")
                print("AMQP features will be disabled. Set force_connection=True to require AMQP connection.")
                self._connected = False
                return

        # Tworzymy kanał
        self.channel = self.connection.channel()

        # Deklarujemy exchange dla zwrotnego publikowania rezultatów
        response_exchange = config.get("response_exchange", "pifunc.responses")
        self.channel.exchange_declare(
            exchange=response_exchange,
            exchange_type=ExchangeType.topic,
            durable=True
        )

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako konsumenta kolejki AMQP."""
        # Jeśli nie jesteśmy połączeni z brokerem, to nie rejestrujemy funkcji
        if not self._connected:
            logger.warning(f"Not connected to AMQP broker, skipping registration of {func.__name__}")
            return

        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację AMQP
        amqp_config = metadata.get("amqp", {})

        # Konfiguracja exchange i kolejki
        exchange = amqp_config.get("exchange", "pifunc.requests")
        exchange_type = amqp_config.get("exchange_type", "topic")
        queue = amqp_config.get("queue", f"pifunc.{service_name}")
        routing_key = amqp_config.get("routing_key", service_name)

        # Właściwości kolejki
        durable = amqp_config.get("durable", True)
        exclusive = amqp_config.get("exclusive", False)
        auto_delete = amqp_config.get("auto_delete", False)

        # Zapisujemy informacje o funkcji
        self.functions[service_name] = {
            "function": func,
            "metadata": metadata,
            "exchange": exchange,
            "exchange_type": exchange_type,
            "queue": queue,
            "routing_key": routing_key,
            "response_routing_key": f"response.{routing_key}",
            "durable": durable,
            "exclusive": exclusive,
            "auto_delete": auto_delete,
            "registered": False
        }

    def _setup_function_queue(self, service_name: str) -> None:
        """Konfiguruje exchange i kolejkę dla konkretnej funkcji."""
        if service_name not in self.functions:
            return

        function_info = self.functions[service_name]

        if function_info.get("registered", False):
            return

        # Deklarujemy exchange
        self.channel.exchange_declare(
            exchange=function_info["exchange"],
            exchange_type=function_info["exchange_type"],
            durable=function_info["durable"]
        )

        # Deklarujemy kolejkę
        self.channel.queue_declare(
            queue=function_info["queue"],
            durable=function_info["durable"],
            exclusive=function_info["exclusive"],
            auto_delete=function_info["auto_delete"]
        )

        # Bindujemy kolejkę do exchange
        self.channel.queue_bind(
            exchange=function_info["exchange"],
            queue=function_info["queue"],
            routing_key=function_info["routing_key"]
        )

        # Oznaczamy jako zarejestrowane
        function_info["registered"] = True

    def _message_callback(self, ch, method, properties, body):
        """Callback obsługujący wiadomości z kolejki."""
        routing_key = method.routing_key

        # Szukamy funkcji obsługującej ten routing key
        target_function = None
        function_info = None

        for name, info in self.functions.items():
            if info["routing_key"] == routing_key:
                target_function = info["function"]
                function_info = info
                break

        if not target_function or not function_info:
            logger.warning(f"No registered function for routing key: {routing_key}")
            # Potwierdzamy odbiór wiadomości, ale nie przetwarzamy jej
            ch.basic_ack(delivery_tag=method.delivery_tag)
            return

        try:
            # Parsujemy JSON
            payload = body.decode('utf-8')
            kwargs = json.loads(payload)

            # Wywołujemy funkcję
            result = target_function(**kwargs)

            # Obsługujemy coroutines
            if asyncio.iscoroutine(result):
                # Tworzymy nową pętlę asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(result)
                loop.close()

            # Przygotowujemy odpowiedź
            response = {
                "result": result,
                "routing_key": routing_key,
                "timestamp": time.time()
            }

            # Publikujemy odpowiedź, jeśli klient oczekuje odpowiedzi (reply_to)
            response_exchange = self.config.get("response_exchange", "pifunc.responses")

            if properties.reply_to:
                # Używamy reply_to podanego przez klienta
                self.channel.basic_publish(
                    exchange="",  # Bezpośrednio do kolejki
                    routing_key=properties.reply_to,
                    properties=pika.BasicProperties(
                        correlation_id=properties.correlation_id,
                        content_type="application/json"
                    ),
                    body=json.dumps(response)
                )
            else:
                # Używamy domyślnego routing key dla odpowiedzi
                self.channel.basic_publish(
                    exchange=response_exchange,
                    routing_key=function_info["response_routing_key"],
                    properties=pika.BasicProperties(
                        content_type="application/json"
                    ),
                    body=json.dumps(response)
                )

            # Potwierdzamy przetworzenie wiadomości
            ch.basic_ack(delivery_tag=method.delivery_tag)

        except json.JSONDecodeError:
            logger.error(f"JSON parsing error: {body}")
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as e:
            # Publikujemy informację o błędzie
            error_response = {
                "error": str(e),
                "routing_key": routing_key,
                "timestamp": time.time()
            }

            response_exchange = self.config.get("response_exchange", "pifunc.responses")
            error_routing_key = f"error.{routing_key}"

            self.channel.basic_publish(
                exchange=response_exchange,
                routing_key=error_routing_key,
                properties=pika.BasicProperties(
                    content_type="application/json",
                    correlation_id=properties.correlation_id if properties else None
                ),
                body=json.dumps(error_response)
            )

            # Potwierdzamy przetworzenie wiadomości (z błędem)
            ch.basic_ack(delivery_tag=method.delivery_tag)
            logger.error(f"Error processing message: {e}")

    def _consume_messages(self):
        """Funkcja wątku konsumującego wiadomości."""
        if not self._connected:
            return

        # Konfigurujemy prefetch (ile wiadomości na raz)
        prefetch_count = self.config.get("prefetch_count", 1)
        self.channel.basic_qos(prefetch_count=prefetch_count)

        # Rozpoczynamy konsumpcję ze wszystkich zarejestrowanych kolejek
        for service_name, function_info in self.functions.items():
            self._setup_function_queue(service_name)

            # Rozpoczynamy konsumpcję
            self.channel.basic_consume(
                queue=function_info["queue"],
                on_message_callback=self._message_callback
            )

        try:
            # Rozpoczynamy konsumpcję wiadomości (blokujące)
            logger.info(f"Started consuming messages from {len(self.functions)} queues")
            print(f"Rozpoczęto konsumpcję wiadomości z {len(self.functions)} kolejek")
            self.channel.start_consuming()
        except Exception as e:
            logger.error(f"Error consuming messages: {e}")
            print(f"Błąd podczas konsumpcji wiadomości: {e}")
        finally:
            try:
                self.channel.stop_consuming()
            except:
                pass

    def start(self) -> None:
        """Uruchamia adapter AMQP."""
        if self.consuming or not self._connected:
            return

        # Zakładamy wątek konsumpcji
        self.consuming = True
        self.consumer_thread = threading.Thread(target=self._consume_messages)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()

        host = self.config.get("host", "localhost")
        port = self.config.get("port", 5672)
        logger.info(f"AMQP adapter started and connected to {host}:{port}")
        print(f"Adapter AMQP uruchomiony i połączony z {host}:{port}")

    def stop(self) -> None:
        """Zatrzymuje adapter AMQP."""
        if not self.consuming or not self._connected:
            return

        self.consuming = False

        # Zatrzymujemy konsumpcję
        try:
            self.channel.stop_consuming()
        except:
            pass

        # Czekamy na zakończenie wątku
        if self.consumer_thread and self.consumer_thread.is_alive():
            self.consumer_thread.join(timeout=2.0)

        # Zamykamy połączenie
        try:
            self.connection.close()
        except:
            pass

        logger.info("AMQP adapter stopped")
        print("Adapter AMQP zatrzymany")