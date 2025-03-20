# Plik: multi_protocol_clients.py
"""
Przykłady klientów dla różnych protokołów komunikacyjnych
"""

import asyncio
import json
import requests
import paho.mqtt.client as mqtt
import websockets
import grpc
import sys


# Przykład klienta HTTP
def http_client_example():
    print("\n=== Przykład klienta HTTP ===")
    base_url = "http://localhost:8080"

    # 1. Tworzenie użytkownika
    user_data = {
        "name": "Tomasz Nowicki",
        "email": "tomasz.nowicki@example.com",
        "age": 42
    }

    response = requests.post(f"{base_url}/api/users", json=user_data)
    user = response.json()["result"]
    print(f"Utworzono użytkownika: {user['name']} (ID: {user['id']})")
    user_id = user["id"]

    # 2. Pobieranie użytkownika
    response = requests.get(f"{base_url}/api/users/{user_id}")
    user = response.json()["result"]
    print(f"Pobrano użytkownika: {user['name']}")

    # 3. Aktualizacja użytkownika
    update_data = {
        "email": "tomasz.nowak@example.com"
    }

    response = requests.put(f"{base_url}/api/users/{user_id}", json=update_data)
    updated_user = response.json()["result"]
    print(f"Zaktualizowano użytkownika: {updated_user['name']}, email: {updated_user['email']}")

    # 4. Wyszukiwanie użytkowników
    response = requests.get(f"{base_url}/api/users/search", params={"min_age": 30})
    users = response.json()["result"]
    print(f"Znaleziono {len(users)} użytkowników w wieku 30+")

    # 5. Usuwanie użytkownika
    response = requests.delete(f"{base_url}/api/users/{user_id}")
    result = response.json()["result"]
    print(f"Usuwanie użytkownika: {result['message']}")


# Przykład klienta MQTT
def mqtt_client_example():
    print("\n=== Przykład klienta MQTT ===")
    client = mqtt.Client()

    # Zmienne do przechowywania odpowiedzi
    responses = {}
    user_id = None

    # Callback wywoływany po połączeniu
    def on_connect(client, userdata, flags, rc):
        print(f"Połączono z brokerem z kodem {rc}")

        # Subskrybujemy tematy odpowiedzi
        client.subscribe("users/create/response")
        client.subscribe("users/get/response")
        client.subscribe("users/update/response")
        client.subscribe("users/list/response")
        client.subscribe("users/delete/response")

    # Callback wywoływany po otrzymaniu wiadomości
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        responses[topic] = payload

    # Ustawiamy callbacki
    client.on_connect = on_connect
    client.on_message = on_message

    # Łączymy się z brokerem
    client.connect("localhost", 1883, 60)
    client.loop_start()

    # Czekamy na nawiązanie połączenia
    import time
    time.sleep(1)

    try:
        # 1. Tworzenie użytkownika
        user_data = {
            "name": "Magdalena Kowalska",
            "email": "magdalena.kowalska@example.com",
            "age": 33
        }

        client.publish("users/create", json.dumps(user_data))

        # Czekamy na odpowiedź
        time.sleep(1)

        if "users/create/response" in responses:
            user = responses["users/create/response"]["result"]
            print(f"Utworzono użytkownika: {user['name']} (ID: {user['id']})")
            user_id = user["id"]

            # 2. Pobieranie użytkownika
            client.publish("users/get", json.dumps({"user_id": user_id}))

            # Czekamy na odpowiedź
            time.sleep(1)

            if "users/get/response" in responses:
                user = responses["users/get/response"]["result"]
                print(f"Pobrano użytkownika: {user['name']}")

                # 3. Aktualizacja użytkownika
                update_data = {
                    "user_id": user_id,
                    "age": 34
                }

                client.publish("users/update", json.dumps(update_data))

                # Czekamy na odpowiedź
                time.sleep(1)

                if "users/update/response" in responses:
                    updated_user = responses["users/update/response"]["result"]
                    print(f"Zaktualizowano użytkownika: {updated_user['name']}, wiek: {updated_user['age']}")

                    # 4. Usuwanie użytkownika
                    client.publish("users/delete", json.dumps({"user_id": user_id}))

                    # Czekamy na odpowiedź
                    time.sleep(1)

                    if "users/delete/response" in responses:
                        result = responses["users/delete/response"]["result"]
                        print(f"Usuwanie użytkownika: {result['message']}")

    finally:
        # Zamykamy klienta
        client.loop_stop()
        client.disconnect()


# Przykład klienta WebSocket
async def websocket_client_example():
    print("\n=== Przykład klienta WebSocket ===")

    async with websockets.connect("ws://localhost:8081") as websocket:
        # 1. Tworzenie użytkownika
        user_data = {
            "event": "user.create",
            "data": {
                "name": "Krzysztof Dąbrowski",
                "email": "krzysztof.dabrowski@example.com",
                "age": 39
            }
        }

        await websocket.send(json.dumps(user_data))
        response = json.loads(await websocket.recv())

        user = response["result"]
        print(f"Utworzono użytkownika: {user['name']} (ID: {user['id']})")
        user_id = user["id"]

        # 2. Pobieranie użytkownika
        get_data = {
            "event": "user.get",
            "data": {
                "user_id": user_id
            }
        }

        await websocket.send(json.dumps(get_data))
        response = json.loads(await websocket.recv())

        user = response["result"]
        print(f"Pobrano użytkownika: {user['name']}")

        # 3. Wyszukiwanie użytkowników
        search_data = {
            "event": "user.search",
            "data": {
                "min_age": 30,
                "max_age": 40
            }
        }

        await websocket.send(json.dumps(search_data))
        response = json.loads(await websocket.recv())

        users = response["result"]
        print(f"Znaleziono {len(users)} użytkowników w wieku 30-40")

        # 4. Usuwanie użytkownika
        delete_data = {
            "event": "user.delete",
            "data": {
                "user_id": user_id
            }
        }

        await websocket.send(json.dumps(delete_data))
        response = json.loads(await websocket.recv())

        result = response["result"]
        print(f"Usuwanie użytkownika: {result['message']}")


# Przykład klienta gRPC
def grpc_client_example():
    print("\n=== Przykład klienta gRPC ===")

    # Importujemy wygenerowane klasy gRPC
    sys.path.append(".pifunc/generated")

    try:
        from create_user_pb2_grpc import create_userServiceStub
        from create_user_pb2 import create_userRequest
        from get_user_pb2_grpc import get_userServiceStub
        from get_user_pb2 import get_userRequest
        from delete_user_pb2_grpc import delete_userServiceStub
        from delete_user_pb2 import delete_userRequest

        # Tworzymy kanał gRPC
        channel = grpc.insecure_channel("localhost:50051")

        # 1. Tworzenie użytkownika
        create_stub = create_userServiceStub(channel)
        create_request = create_userRequest(
            name="Alicja Malinowska",
            email="alicja.malinowska@example.com",
            age=27
        )

        create_response = create_stub.Create_user(create_request)
        user_id = create_response.result["id"]
        print(f"Utworzono użytkownika: {create_response.result['name']} (ID: {user_id})")

        # 2. Pobieranie użytkownika
        get_stub = get_userServiceStub(channel)
        get_request = get_userRequest(
            user_id=user_id
        )

        get_response = get_stub.Get_user(get_request)
        print(f"Pobrano użytkownika: {get_response.result['name']}")

        # 3. Usuwanie użytkownika
        delete_stub = delete_userServiceStub(channel)
        delete_request = delete_userRequest(
            user_id=user_id
        )

        delete_response = delete_stub.Delete_user(delete_request)
        print(f"Usuwanie użytkownika: {delete_response.result['message']}")

    except ImportError as e:
        print(f"Błąd importu wygenerowanych klas gRPC: {e}")
        print("Uruchom najpierw serwer, aby wygenerować klasy gRPC.")

    except Exception as e:
        print(f"Wystąpił błąd: {e}")


# Funkcja główna
def main():
    print("Przykłady klientów dla różnych protokołów")

    # HTTP client
    try:
        http_client_example()
    except Exception as e:
        print(f"Błąd klienta HTTP: {e}")

    # MQTT client
    try:
        mqtt_client_example()
    except Exception as e:
        print(f"Błąd klienta MQTT: {e}")

    # WebSocket client
    try:
        asyncio.run(websocket_client_example())
    except Exception as e:
        print(f"Błąd klienta WebSocket: {e}")

    # gRPC client
    try:
        grpc_client_example()
    except Exception as e:
        print(f"Błąd klienta gRPC: {e}")


if __name__ == "__main__":
    main()