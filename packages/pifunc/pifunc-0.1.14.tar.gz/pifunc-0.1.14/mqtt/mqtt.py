import os
from pifunc import service, run_services, mqtt_client, demo_mqtt
from dotenv import load_dotenv  # If needed
# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables with defaults
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", 8081))

# Pojedynczy dekorator @service definiuje usługę dostępną przez różne protokoły
@service(
    # Domyślnie włączone są wszystkie protokoły, ale można je selektywnie włączać/wyłączać
    protocols=["grpc", "http", "mqtt"],
    # Konfiguracja dla MQTT
    mqtt={
        "topic": "calculator/add",
        # Automatyczna serializacja wyników do JSON
        "qos": 1
    },
)
def add(a: int, b: int) -> int:
    """Dodaje dwie liczby."""
    return a + b


@service(
    mqtt={"topic": "calculator/subtract"},
)
def subtract(a: int, b: int) -> int:
    """Odejmuje liczbę b od liczby a."""
    return a - b


@service(
    mqtt={"topic": "calculator/multiply"},
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
#if __name__ == "__main__":

async def main():
    """Run all protocol demonstrations."""
    print("Starting protocol demonstrations...")

    # Uruchamiamy wszystkie zarejestrowane usługi
    run_services(
        # Możemy skonfigurować wszystkie protokoły
        mqtt={"broker": "localhost", "port": 1883},
        # Włączamy hot-reload
        watch=True
    )

    try:
        await demo_mqtt()
    except Exception as e:
        print(f"MQTT demo error: {e}")


    async with mqtt_client.connect("mqtt://localhost:1883") as mqtt:
        await mqtt.publish("calculator/add", {"a": 20, "b": 10})
        result = await mqtt.subscribe("calculator/result")
        print(result)  # 30