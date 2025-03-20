# clients_examples.py
"""
Skrypt zawierający przykłady klientów dla różnych protokołów komunikacyjnych.
Pokazuje, jak wywoływać tę samą logikę biznesową za pomocą różnych protokołów.
"""

import json
import asyncio
import sys
import uuid
import time

####### 1. HTTP Client #######

async def http_client_example():
    """Przykład klienta HTTP."""
    import aiohttp
    
    print("\n=== HTTP Client Example ===")
    base_url = "http://localhost:8080/api"
    
    async with aiohttp.ClientSession() as session:
        # 1. Tworzenie nowego zadania
        task_data = {
            "title": "Zadanie z HTTP",
            "description": "Przykładowe zadanie utworzone przez klienta HTTP"
        }
        
        print("Tworzenie zadania...")
        async with session.post(f"{base_url}/tasks", json=task_data) as response:
            result = await response.json()
            task = result["result"]
            task_id = task["id"]
            print(f"Utworzono zadanie: {task['title']} (ID: {task_id})")
        
        # 2. Pobieranie zadania
        print("Pobieranie zadania...")
        async with session.get(f"{base_url}/tasks/{task_id}") as response:
            result = await response.json()
            task = result["result"]
            print(f"Pobrano zadanie: {task['title']} - {task['description']}")
        
        # 3. Aktualizacja zadania
        update_data = {
            "completed": True
        }
        
        print("Aktualizacja zadania...")
        async with session.put(f"{base_url}/tasks/{task_id}", json=update_data) as response:
            result = await response.json()
            task = result["result"]
            print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
        
        # 4. Pobieranie listy zadań
        print("Pobieranie listy zadań...")
        async with session.get(f"{base_url}/tasks") as response:
            result = await response.json()
            tasks = result["result"]
            print(f"Pobrano {len(tasks)} zadań:")
            for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
                print(f"  {idx}. {t['title']} - {t['completed']}")
            if len(tasks) > 3:
                print(f"  ... i {len(tasks) - 3} więcej")
        
        # 5. Usuwanie zadania
        print("Usuwanie zadania...")
        async with session.delete(f"{base_url}/tasks/{task_id}") as response:
            result = await response.json()
            print(f"Wynik usuwania: {result['result']['message']}")

####### 2. gRPC Client #######

async def grpc_client_example():
    """Przykład klienta gRPC."""
    print("\n=== gRPC Client Example ===")
    
    try:
        import grpc
        
        # Sprawdzamy, czy ścieżka do wygenerowanych plików jest dostępna
        sys.path.append('.pifunc/generated')
        
        # Importujemy wygenerowane klasy gRPC
        from create_task_pb2_grpc import create_taskServiceStub
        from create_task_pb2 import create_taskRequest
        from get_task_pb2_grpc import get_taskServiceStub
        from get_task_pb2 import get_taskRequest
        from update_task_pb2_grpc import update_taskServiceStub
        from update_task_pb2 import update_taskRequest
        from list_tasks_pb2_grpc import list_tasksServiceStub
        from list_tasks_pb2 import list_tasksRequest
        from delete_task_pb2_grpc import delete_taskServiceStub
        from delete_task_pb2 import delete_taskRequest
        
        # Tworzymy kanał gRPC
        channel = grpc.insecure_channel("localhost:50051")
        
        # 1. Tworzenie nowego zadania
        create_stub = create_taskServiceStub(channel)
        create_request = create_taskRequest(
            title="Zadanie z gRPC",
            description="Przykładowe zadanie utworzone przez klienta gRPC"
        )
        
        print("Tworzenie zadania...")
        create_response = create_stub.Create_task(create_request)
        task_id = json.loads(create_response.result)["id"]
        print(f"Utworzono zadanie z ID: {task_id}")
        
        # 2. Pobieranie zadania
        get_stub = get_taskServiceStub(channel)
        get_request = get_taskRequest(task_id=task_id)
        
        print("Pobieranie zadania...")
        get_response = get_stub.Get_task(get_request)
        task = json.loads(get_response.result)
        print(f"Pobrano zadanie: {task['title']} - {task['description']}")
        
        # 3. Aktualizacja zadania
        update_stub = update_taskServiceStub(channel)
        update_request = update_taskRequest(
            task_id=task_id,
            completed="true"  # W gRPC przekazujemy jako string
        )
        
        print("Aktualizacja zadania...")
        update_response = update_stub.Update_task(update_request)
        task = json.loads(update_response.result)
        print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
        
        # 4. Pobieranie listy zadań
        list_stub = list_tasksServiceStub(channel)
        list_request = list_tasksRequest(offset=0, limit=10)
        
        print("Pobieranie listy zadań...")
        list_response = list_stub.List_tasks(list_request)
        tasks = json.loads(list_response.result)
        print(f"Pobrano {len(tasks)} zadań:")
        for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
            print(f"  {idx}. {t['title']} - {t['completed']}")
        if len(tasks) > 3:
            print(f"  ... i {len(tasks) - 3} więcej")
        
        # 5. Usuwanie zadania
        delete_stub = delete_taskServiceStub(channel)
        delete_request = delete_taskRequest(task_id=task_id)
        
        print("Usuwanie zadania...")
        delete_response = delete_stub.Delete_task(delete_request)
        result = json.loads(delete_response.result)
        print(f"Wynik usuwania: {result['message']}")
        
    except ImportError as e:
        print(f"Błąd importu: {e}")
        print("Upewnij się, że serwer gRPC jest uruchomiony, aby wygenerowane pliki były dostępne.")
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

####### 3. MQTT Client #######

async def mqtt_client_example():
    """Przykład klienta MQTT."""
    import paho.mqtt.client as mqtt
    
    print("\n=== MQTT Client Example ===")
    
    # Tworzymy ID klienta
    client_id = f"pifunc-client-{uuid.uuid4().hex[:8]}"
    
    # Słownik na odpowiedzi
    responses = {}
    response_event = asyncio.Event()
    
    # Callback wywoływany po połączeniu
    def on_connect(client, userdata, flags, rc):
        print(f"Połączono z brokerem MQTT z kodem {rc}")
        
        # Subskrybujemy tematy odpowiedzi
        client.subscribe("tasks/create/response")
        client.subscribe("tasks/get/response")
        client.subscribe("tasks/update/response")
        client.subscribe("tasks/list/response")
        client.subscribe("tasks/delete/response")
        
        # Subskrybujemy też tematy błędów
        client.subscribe("tasks/create/error")
        client.subscribe("tasks/get/error")
        client.subscribe("tasks/update/error")
        client.subscribe("tasks/list/error")
        client.subscribe("tasks/delete/error")
    
    # Callback wywoływany po otrzymaniu wiadomości
    def on_message(client, userdata, msg):
        topic = msg.topic
        payload = json.loads(msg.payload.decode())
        
        # Zapisujemy odpowiedź
        responses[topic] = payload
        
        # Sygnalizujemy, że otrzymaliśmy odpowiedź
        response_event.set()
    
    # Tworzymy klienta
    client = mqtt.Client(client_id=client_id)
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Łączymy się z brokerem
    client.connect("localhost", 1883, 60)
    client.loop_start()
    
    # Czekamy na nawiązanie połączenia
    await asyncio.sleep(1)
    
    try:
        # 1. Tworzenie zadania
        task_data = {
            "title": "Zadanie z MQTT",
            "description": "Przykładowe zadanie utworzone przez klienta MQTT"
        }
        
        print("Tworzenie zadania...")
        response_event.clear()
        client.publish("tasks/create", json.dumps(task_data))
        
        # Czekamy na odpowiedź
        await asyncio.wait_for(response_event.wait(), timeout=5.0)
        
        if "tasks/create/response" in responses:
            result = responses["tasks/create/response"]["result"]
            task_id = result["id"]
            print(f"Utworzono zadanie: {result['title']} (ID: {task_id})")
            
            # 2. Pobieranie zadania
            print("Pobieranie zadania...")
            response_event.clear()
            client.publish("tasks/get", json.dumps({"task_id": task_id}))
            
            # Czekamy na odpowiedź
            await asyncio.wait_for(response_event.wait(), timeout=5.0)
            
            if "tasks/get/response" in responses:
                task = responses["tasks/get/response"]["result"]
                print(f"Pobrano zadanie: {task['title']} - {task['description']}")
                
                # 3. Aktualizacja zadania
                update_data = {
                    "task_id": task_id,
                    "completed": True
                }
                
                print("Aktualizacja zadania...")
                response_event.clear()
                client.publish("tasks/update", json.dumps(update_data))
                
                # Czekamy na odpowiedź
                await asyncio.wait_for(response_event.wait(), timeout=5.0)
                
                if "tasks/update/response" in responses:
                    task = responses["tasks/update/response"]["result"]
                    print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
                    
                    # 4. Pobieranie listy zadań
                    print("Pobieranie listy zadań...")
                    response_event.clear()
                    client.publish("tasks/list", json.dumps({"offset": 0, "limit": 10}))
                    
                    # Czekamy na odpowiedź
                    await asyncio.wait_for(response_event.wait(), timeout=5.0)
                    
                    if "tasks/list/response" in responses:
                        tasks = responses["tasks/list/response"]["result"]
                        print(f"Pobrano {len(tasks)} zadań:")
                        for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
                            print(f"  {idx}. {t['title']} - {t['completed']}")
                        if len(tasks) > 3:
                            print(f"  ... i {len(tasks) - 3} więcej")
                        
                        # 5. Usuwanie zadania
                        print("Usuwanie zadania...")
                        response_event.clear()
                        client.publish("tasks/delete", json.dumps({"task_id": task_id}))
                        
                        # Czekamy na odpowiedź
                        await asyncio.wait_for(response_event.wait(), timeout=5.0)
                        
                        if "tasks/delete/response" in responses:
                            result = responses["tasks/delete/response"]["result"]
                            print(f"Wynik usuwania: {result['message']}")
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")
    finally:
        # Zamykamy klienta
        client.loop_stop()
        client.disconnect()

####### 4. WebSocket Client #######

async def websocket_client_example():
    """Przykład klienta WebSocket."""
    import websockets
    
    print("\n=== WebSocket Client Example ===")
    
    try:
        # Łączymy się z serwerem WebSocket
        async with websockets.connect("ws://localhost:8081/tasks") as websocket:
            # Czekamy na wiadomość powitalną
            welcome_message = await websocket.recv()
            print(f"Otrzymano wiadomość: {welcome_message}")
            
            # 1. Tworzenie zadania
            task_data = {
                "event": "tasks.create",
                "data": {
                    "title": "Zadanie z WebSocket",
                    "description": "Przykładowe zadanie utworzone przez klienta WebSocket"
                }
            }
            
            print("Tworzenie zadania...")
            await websocket.send(json.dumps(task_data))
            response = json.loads(await websocket.recv())
            
            task = response["result"]
            task_id = task["id"]
            print(f"Utworzono zadanie: {task['title']} (ID: {task_id})")
            
            # 2. Pobieranie zadania
            get_data = {
                "event": "tasks.get",
                "data": {
                    "task_id": task_id
                }
            }
            
            print("Pobieranie zadania...")
            await websocket.send(json.dumps(get_data))
            response = json.loads(await websocket.recv())
            
            task = response["result"]
            print(f"Pobrano zadanie: {task['title']} - {task['description']}")
            
            # 3. Aktualizacja zadania
            update_data = {
                "event": "tasks.update",
                "data": {
                    "task_id": task_id,
                    "completed": True
                }
            }
            
            print("Aktualizacja zadania...")
            await websocket.send(json.dumps(update_data))
            response = json.loads(await websocket.recv())
            
            task = response["result"]
            print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
            
            # 4. Pobieranie listy zadań
            list_data = {
                "event": "tasks.list",
                "data": {
                    "offset": 0,
                    "limit": 10
                }
            }
            
            print("Pobieranie listy zadań...")
            await websocket.send(json.dumps(list_data))
            response = json.loads(await websocket.recv())
            
            tasks = response["result"]
            print(f"Pobrano {len(tasks)} zadań:")
            for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
                print(f"  {idx}. {t['title']} - {t['completed']}")
            if len(tasks) > 3:
                print(f"  ... i {len(tasks) - 3} więcej")
            
            # 5. Usuwanie zadania
            delete_data = {
                "event": "tasks.delete",
                "data": {
                    "task_id": task_id
                }
            }
            
            print("Usuwanie zadania...")
            await websocket.send(json.dumps(delete_data))
            response = json.loads(await websocket.recv())
            
            result = response["result"]
            print(f"Wynik usuwania: {result['message']}")
            
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

####### 5. GraphQL Client #######

async def graphql_client_example():
    """Przykład klienta GraphQL."""
    import aiohttp
    
    print("\n=== GraphQL Client Example ===")
    
    graphql_url = "http://localhost:8082/graphql"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. Tworzenie zadania
            create_mutation = """
            mutation {
                createTask(title: "Zadanie z GraphQL", description: "Przykładowe zadanie utworzone przez klienta GraphQL") {
                    result {
                        id
                        title
                        description
                    }
                }
            }
            """
            
            print("Tworzenie zadania...")
            async with session.post(
                graphql_url,
                json={"query": create_mutation}
            ) as response:
                result = await response.json()
                task = result["data"]["createTask"]["result"]
                task_id = task["id"]
                print(f"Utworzono zadanie: {task['title']} (ID: {task_id})")
            
            # 2. Pobieranie zadania
            get_query = f"""
            query {{
                task(task_id: "{task_id}") {{
                    result {{
                        id
                        title
                        description
                        completed
                    }}
                }}
            }}
            """
            
            print("Pobieranie zadania...")
            async with session.post(
                graphql_url,
                json={"query": get_query}
            ) as response:
                result = await response.json()
                task = result["data"]["task"]["result"]
                print(f"Pobrano zadanie: {task['title']} - {task['description']}")
            
            # 3. Aktualizacja zadania
            update_mutation = f"""
            mutation {{
                updateTask(task_id: "{task_id}", completed: true) {{
                    result {{
                        id
                        title
                        completed
                    }}
                }}
            }}
            """
            
            print("Aktualizacja zadania...")
            async with session.post(
                graphql_url,
                json={"query": update_mutation}
            ) as response:
                result = await response.json()
                task = result["data"]["updateTask"]["result"]
                print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
            
            # 4. Pobieranie listy zadań
            list_query = """
            query {
                tasks(offset: 0, limit: 10) {
                    result {
                        id
                        title
                        completed
                    }
                }
            }
            """
            
            print("Pobieranie listy zadań...")
            async with session.post(
                graphql_url,
                json={"query": list_query}
            ) as response:
                result = await response.json()
                tasks = result["data"]["tasks"]["result"]
                print(f"Pobrano {len(tasks)} zadań:")
                for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
                    print(f"  {idx}. {t['title']} - {t['completed']}")
                if len(tasks) > 3:
                    print(f"  ... i {len(tasks) - 3} więcej")
            
            # 5. Usuwanie zadania
            delete_mutation = f"""
            mutation {{
                deleteTask(task_id: "{task_id}") {{
                    result {{
                        message
                    }}
                }}
            }}
            """
            
            print("Usuwanie zadania...")
            async with session.post(
                graphql_url,
                json={"query": delete_mutation}
            ) as response:
                result = await response.json()
                message = result["data"]["deleteTask"]["result"]["message"]
                print(f"Wynik usuwania: {message}")
                
        except Exception as e:
            print(f"Wystąpił błąd: {e}")

####### 6. Redis Client #######

async def redis_client_example():
    """Przykład klienta Redis."""
    import redis
    
    print("\n=== Redis Client Example ===")
    
    try:
        # Tworzymy klienta Redis
        r = redis.Redis(host="localhost", port=6379, decode_responses=True)
        
        # Tworzymy unikalne ID dla korelacji wiadomości
        correlation_id = str(uuid.uuid4())
        
        # 1. Tworzenie zadania
        task_data = {
            "title": "Zadanie z Redis",
            "description": "Przykładowe zadanie utworzone przez klienta Redis",
            "correlation_id": correlation_id
        }
        
        print("Tworzenie zadania...")
        
        # Subskrybujemy kanał odpowiedzi
        pubsub = r.pubsub()
        pubsub.subscribe("tasks:create:response")
        
        # Publikujemy żądanie
        r.publish("tasks:create", json.dumps(task_data))
        
        # Odbieramy odpowiedź (w rzeczywistej aplikacji powinno być z timeoutem)
        task_id = None
        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])
                result = data["result"]
                task_id = result["id"]
                print(f"Utworzono zadanie: {result['title']} (ID: {task_id})")
                break
        
        # Odsubskrybujemy i subskrybujemy następny kanał
        pubsub.unsubscribe()
        
        if task_id:
            # 2. Pobieranie zadania
            get_data = {
                "task_id": task_id,
                "correlation_id": correlation_id
            }
            
            print("Pobieranie zadania...")
            pubsub.subscribe("tasks:get:response")
            
            # Publikujemy żądanie
            r.publish("tasks:get", json.dumps(get_data))
            
            # Odbieramy odpowiedź
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    task = data["result"]
                    print(f"Pobrano zadanie: {task['title']} - {task['description']}")
                    break
            
            # Odsubskrybujemy i subskrybujemy następny kanał
            pubsub.unsubscribe()
            
            # 3. Aktualizacja zadania
            update_data = {
                "task_id": task_id,
                "completed": True,
                "correlation_id": correlation_id
            }
            
            print("Aktualizacja zadania...")
            pubsub.subscribe("tasks:update:response")
            
            # Publikujemy żądanie
            r.publish("tasks:update", json.dumps(update_data))
            
            # Odbieramy odpowiedź
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    task = data["result"]
                    print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
                    break
            
            # Odsubskrybujemy i subskrybujemy następny kanał
            pubsub.unsubscribe()
            
            # 4. Pobieranie listy zadań
            list_data = {
                "offset": 0,
                "limit": 10,
                "correlation_id": correlation_id
            }
            
            print("Pobieranie listy zadań...")
            pubsub.subscribe("tasks:list:response")
            
            # Publikujemy żądanie
            r.publish("tasks:list", json.dumps(list_data))
            
            # Odbieramy odpowiedź
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    tasks = data["result"]
                    print(f"Pobrano {len(tasks)} zadań:")
                    for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
                        print(f"  {idx}. {t['title']} - {t['completed']}")
                    if len(tasks) > 3:
                        print(f"  ... i {len(tasks) - 3} więcej")
                    break
            
            # Odsubskrybujemy i subskrybujemy następny kanał
            pubsub.unsubscribe()
            
            # 5. Usuwanie zadania
            delete_data = {
                "task_id": task_id,
                "correlation_id": correlation_id
            }
            
            print("Usuwanie zadania...")
            pubsub.subscribe("tasks:delete:response")
            
            # Publikujemy żądanie
            r.publish("tasks:delete", json.dumps(delete_data))
            
            # Odbieramy odpowiedź
            for message in pubsub.listen():
                if message["type"] == "message":
                    data = json.loads(message["data"])
                    result = data["result"]
                    print(f"Wynik usuwania: {result['message']}")
                    break
            
            # Odsubskrybujemy
            pubsub.unsubscribe()
        
        # Zamykamy połączenie
        pubsub.close()
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

####### 7. ZeroMQ Client #######

async def zeromq_client_example():
    """Przykład klienta ZeroMQ."""
    import zmq
    
    print("\n=== ZeroMQ Client Example ===")
    
    try:
        # Tworzymy kontekst ZeroMQ
        context = zmq.Context()
        
        # Tworzymy gniazdo REQ dla funkcji create_task
        socket_create = context.socket(zmq.REQ)
        socket_create.connect("tcp://localhost:5557")
        
        # 1. Tworzenie zadania
        task_data = {
            "title": "Zadanie z ZeroMQ",
            "description": "Przykładowe zadanie utworzone przez klienta ZeroMQ"
        }
        
        print("Tworzenie zadania...")
        socket_create.send_string(json.dumps(task_data))
        
        # Odbieramy odpowiedź
        response = socket_create.recv_string()
        result = json.loads(response)["result"]
        task_id = result["id"]
        print(f"Utworzono zadanie: {result['title']} (ID: {task_id})")
        
        # Zamykamy gniazdo
        socket_create.close()
        
        # Tworzymy gniazdo REQ dla funkcji get_task
        socket_get = context.socket(zmq.REQ)
        socket_get.connect("tcp://localhost:5556")
        
        # 2. Pobieranie zadania
        get_data = {
            "task_id": task_id
        }
        
        print("Pobieranie zadania...")
        socket_get.send_string(json.dumps(get_data))
        
        # Odbieramy odpowiedź
        response = socket_get.recv_string()
        task = json.loads(response)["result"]
        print(f"Pobrano zadanie: {task['title']} - {task['description']}")
        
        # Zamykamy gniazdo
        socket_get.close()
        
        # Tworzymy gniazdo REQ dla funkcji update_task
        socket_update = context.socket(zmq.REQ)
        socket_update.connect("tcp://localhost:5558")
        
        # 3. Aktualizacja zadania
        update_data = {
            "task_id": task_id,
            "completed": True
        }
        
        print("Aktualizacja zadania...")
        socket_update.send_string(json.dumps(update_data))
        
        # Odbieramy odpowiedź
        response = socket_update.recv_string()
        task = json.loads(response)["result"]
        print(f"Zaktualizowano zadanie: {task['title']} (ukończone: {task['completed']})")
        
        # Zamykamy gniazdo
        socket_update.close()
        
        # Tworzymy gniazdo REQ dla funkcji list_tasks
        socket_list = context.socket(zmq.REQ)
        socket_list.connect("tcp://localhost:5555")
        
        # 4. Pobieranie listy zadań
        list_data = {
            "offset": 0,
            "limit": 10
        }
        
        print("Pobieranie listy zadań...")
        socket_list.send_string(json.dumps(list_data))
        
        # Odbieramy odpowiedź
        response = socket_list.recv_string()
        tasks = json.loads(response)["result"]
        print(f"Pobrano {len(tasks)} zadań:")
        for idx, t in enumerate(tasks[:3], 1):  # Pokazujemy tylko 3 pierwsze
            print(f"  {idx}. {t['title']} - {t['completed']}")
        if len(tasks) > 3:
            print(f"  ... i {len(tasks) - 3} więcej")
        
        # Zamykamy gniazdo
        socket_list.close()
        
        # Tworzymy gniazdo REQ dla funkcji delete_task
        socket_delete = context.socket(zmq.REQ)
        socket_delete.connect("tcp://localhost:5559")
        
        # 5. Usuwanie zadania
        delete_data = {
            "task_id": task_id
        }
        
        print("Usuwanie zadania...")
        socket_delete.send_string(json.dumps(delete_data))
        
        # Odbieramy odpowiedź
        response = socket_delete.recv_string()
        result = json.loads(response)["result"]
        print(f"Wynik usuwania: {result['message']}")
        
        # Zamykamy gniazdo
        socket_delete.close()
        
        # Zamykamy kontekst
        context.term()
        
    except Exception as e:
        print(f"Wystąpił błąd: {e}")

####### Main Function #######

async def main():
    """Główna funkcja testująca różne protokoły."""
    print("======== PIfunc - Przykłady klientów dla różnych protokołów ========")
    
    # Uruchamiamy przykłady klientów
    await http_client_example()
    await grpc_client_example()
    await mqtt_client_example()
    await websocket_client_example()
    await graphql_client_example()
    await redis_client_example()
    await zeromq_client_example()
    
    print("\n======== Koniec testów ========")

if __name__ == "__main__":
    asyncio.run(main())