# multi_protocol_service.py
from pifunc import service, run_services
from dataclasses import dataclass
from typing import List, Dict, Optional
import uuid
import time

# Baza danych z zadaniami (in-memory)
tasks_db = {}


@dataclass
class Task:
    id: str
    title: str
    description: str
    completed: bool = False
    created_at: float = 0.0
    updated_at: float = 0.0


@service(
    # Konfiguracja dla HTTP
    http={
        "path": "/api/tasks",
        "method": "GET"
    },
    # Konfiguracja dla gRPC
    grpc={
        "streaming": False
    },
    # Konfiguracja dla MQTT
    mqtt={
        "topic": "tasks/list",
        "qos": 1
    },
    # Konfiguracja dla WebSocket
    websocket={
        "event": "tasks.list",
        "namespace": "/tasks"
    },
    # Konfiguracja dla GraphQL
    graphql={
        "field_name": "tasks",
        "description": "Pobiera listę zadań"
    },
    # Konfiguracja dla Redis
    redis={
        "channel": "tasks:list",
        "pattern": False
    },
    # Konfiguracja dla AMQP
    amqp={
        "exchange": "pifunc.requests",
        "queue": "pifunc.tasks.list",
        "routing_key": "tasks.list"
    },
    # Konfiguracja dla ZeroMQ
    zeromq={
        "pattern": "REQ_REP",
        "port": 5555
    },
    # Konfiguracja dla REST
    rest={
        "path": "/tasks",
        "methods": ["GET"]
    }
)
def list_tasks(offset: int = 0, limit: int = 10) -> List[Dict]:
    """Pobiera listę zadań."""
    tasks = list(tasks_db.values())
    paginated_tasks = tasks[offset:offset + limit]
    return [task.__dict__ for task in paginated_tasks]


@service(
    http={"path": "/api/tasks/{task_id}", "method": "GET"},
    mqtt={"topic": "tasks/get"},
    websocket={"event": "tasks.get"},
    graphql={"field_name": "task"},
    redis={"channel": "tasks:get"},
    amqp={"routing_key": "tasks.get"},
    zeromq={"pattern": "REQ_REP", "port": 5556},
    rest={"path": "/tasks/{task_id}", "methods": ["GET"]}
)
def get_task(task_id: str) -> Dict:
    """Pobiera szczegóły zadania."""
    if task_id not in tasks_db:
        raise ValueError(f"Zadanie o ID {task_id} nie istnieje")

    return tasks_db[task_id].__dict__


@service(
    http={"path": "/api/tasks", "method": "POST"},
    mqtt={"topic": "tasks/create"},
    websocket={"event": "tasks.create"},
    graphql={"field_name": "createTask", "is_mutation": True},
    redis={"channel": "tasks:create"},
    amqp={"routing_key": "tasks.create"},
    zeromq={"pattern": "REQ_REP", "port": 5557},
    rest={"path": "/tasks", "methods": ["POST"]}
)
def create_task(title: str, description: str) -> Dict:
    """Tworzy nowe zadanie."""
    task_id = str(uuid.uuid4())
    now = time.time()

    # Tworzymy nowe zadanie
    task = Task(
        id=task_id,
        title=title,
        description=description,
        completed=False,
        created_at=now,
        updated_at=now
    )

    # Zapisujemy w bazie danych
    tasks_db[task_id] = task

    return task.__dict__


@service(
    http={"path": "/api/tasks/{task_id}", "method": "PUT"},
    mqtt={"topic": "tasks/update"},
    websocket={"event": "tasks.update"},
    graphql={"field_name": "updateTask", "is_mutation": True},
    redis={"channel": "tasks:update"},
    amqp={"routing_key": "tasks.update"},
    zeromq={"pattern": "REQ_REP", "port": 5558},
    rest={"path": "/tasks/{task_id}", "methods": ["PUT"]}
)
def update_task(
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
) -> Dict:
    """Aktualizuje dane zadania."""
    if task_id not in tasks_db:
        raise ValueError(f"Zadanie o ID {task_id} nie istnieje")

    task = tasks_db[task_id]

    # Aktualizujemy tylko podane pola
    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if completed is not None:
        task.completed = completed

    # Aktualizujemy czas
    task.updated_at = time.time()

    # Zapisujemy zaktualizowane dane
    tasks_db[task_id] = task

    return task.__dict__


@service(
    http={"path": "/api/tasks/{task_id}", "method": "DELETE"},
    mqtt={"topic": "tasks/delete"},
    websocket={"event": "tasks.delete"},
    graphql={"field_name": "deleteTask", "is_mutation": True},
    redis={"channel": "tasks:delete"},
    amqp={"routing_key": "tasks.delete"},
    zeromq={"pattern": "REQ_REP", "port": 5559},
    rest={"path": "/tasks/{task_id}", "methods": ["DELETE"]}
)
def delete_task(task_id: str) -> Dict:
    """Usuwa zadanie."""
    if task_id not in tasks_db:
        raise ValueError(f"Zadanie o ID {task_id} nie istnieje")

    # Usuwamy zadanie
    task = tasks_db.pop(task_id)

    return {
        "success": True,
        "message": f"Zadanie o ID {task_id} zostało usunięte",
        "task": task.__dict__
    }


# Funkcja tworząca przykładowe zadania
def create_sample_tasks():
    # Usuwamy wszystkie zadania
    tasks_db.clear()

    # Tworzymy kilka przykładowych zadań
    sample_tasks = [
        {"title": "Zakupy spożywcze", "description": "Kupić mleko, chleb i warzywa"},
        {"title": "Spotkanie projektowe", "description": "Przygotować prezentację na spotkanie"},
        {"title": "Trening", "description": "Iść na siłownię"},
        {"title": "Lektura", "description": "Przeczytać rozdział książki"},
        {"title": "Nauka", "description": "Powtórzyć materiał na egzamin"}
    ]

    for task_data in sample_tasks:
        create_task(**task_data)

    print(f"Utworzono {len(sample_tasks)} przykładowych zadań")


# Gdy uruchamiamy plik bezpośrednio, startujemy wszystkie protokoły
if __name__ == "__main__":
    # Tworzymy przykładowe zadania
    create_sample_tasks()

    # Uruchamiamy wszystkie zarejestrowane usługi
    run_services(
        # Konfiguracja HTTP
        http={"port": 8080, "cors": True},

        # Konfiguracja gRPC
        grpc={"port": 50051, "reflection": True},

        # Konfiguracja MQTT
        mqtt={"broker": "localhost", "port": 1883},

        # Konfiguracja WebSocket
        websocket={"port": 8081},

        # Konfiguracja GraphQL
        graphql={"port": 8082, "playground": True},

        # Konfiguracja Redis
        redis={"host": "localhost", "port": 6379},

        # Konfiguracja AMQP (RabbitMQ)
        amqp={"host": "localhost", "port": 5672},

        # Konfiguracja ZeroMQ
        zeromq={},

        # Konfiguracja REST
        rest={"port": 8000},

        # Włączamy auto-reload
        watch=True
    )