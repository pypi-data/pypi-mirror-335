# simple_service.py
from pifunc import service, run_services


# Pojedynczy dekorator @service definiuje usługę dostępną przez różne protokoły
@service(
    # Domyślnie włączone są wszystkie protokoły, ale można je selektywnie włączać/wyłączać
    protocols=["grpc", "http", "mqtt", "websocket", "graphql"],
    # Konfiguracja dla HTTP
    http={
        "path": "/api/calculator/add",
        "method": "POST",
        # Automatyczna konwersja parametrów z JSON
        "content_type": "application/json"
    },
    # Konfiguracja dla MQTT
    mqtt={
        "topic": "calculator/add",
        # Automatyczna serializacja wyników do JSON
        "qos": 1
    },
    # Konfiguracja dla WebSocket
    websocket={
        "event": "calculator.add"
    },
    # Konfiguracja dla GraphQL
    graphql={
        "field_name": "add",
        "description": "Dodaje dwie liczby"
    }
)
def add(a: int, b: int) -> int:
    """Dodaje dwie liczby."""
    return a + b


@service(
    http={"path": "/api/calculator/subtract", "method": "POST"},
    mqtt={"topic": "calculator/subtract"},
    websocket={"event": "calculator.subtract"},
    graphql={"field_name": "subtract"}
)
def subtract(a: int, b: int) -> int:
    """Odejmuje liczbę b od liczby a."""
    return a - b


@service(
    http={"path": "/api/calculator/multiply", "method": "POST"},
    mqtt={"topic": "calculator/multiply"},
    websocket={"event": "calculator.multiply"},
    graphql={"field_name": "multiply"}
)
def multiply(a: int, b: int) -> int:
    """Mnoży dwie liczby."""
    return a * b


# Można też konfigurować każdy protokół osobno i dodawać specyficzne metadane
@service()
def divide(a: float, b: float) -> float:
    """Dzieli liczbę a przez liczbę b."""
    if b == 0:
        raise ValueError("Nie można dzielić przez zero")
    return a / b


# Gdy uruchamiamy plik bezpośrednio, startujemy wszystkie serwery
if __name__ == "__main__":
    # Uruchamiamy wszystkie zarejestrowane usługi
    run_services(
        # Możemy skonfigurować wszystkie protokoły
        grpc={"port": 50051, "reflection": True},
        http={"port": 8080, "cors": True},
        mqtt={"broker": "localhost", "port": 1883},
        websocket={"port": 8081},
        graphql={"port": 8082, "playground": True},

        # Włączamy hot-reload
        watch=True
    )