# advanced_service.py
from pifunc import service, run_services
from typing import List, Dict, Optional
from dataclasses import dataclass
import json


# Definiujemy model danych
@dataclass
class User:
    id: str
    name: str
    email: str
    age: int


# Prosta "baza danych" użytkowników
users_db = {}


# Funkcja pomocnicza do generowania ID
def generate_id():
    import uuid
    return str(uuid.uuid4())


# Rejestrujemy funkcję tworzenia użytkownika dostępną przez różne protokoły
@service(
    name="create_user",
    description="Tworzy nowego użytkownika",
    # Konfiguracja dla HTTP REST
    http={
        "path": "/api/users",
        "method": "POST",
        "status_code": 201  # Created
    },
    # Konfiguracja dla MQTT
    mqtt={
        "topic": "users/create",
        "qos": 1
    },
    # Konfiguracja dla WebSocket
    websocket={
        "event": "user.create"
    },
    # Konfiguracja dla GraphQL
    graphql={
        "field_name": "createUser",
        "description": "Tworzy nowego użytkownika"
    }
)
def create_user(name: str, email: str, age: int) -> Dict:
    """Tworzy nowego użytkownika."""
    user_id = generate_id()

    # Tworzymy nowego użytkownika
    user = {
        "id": user_id,
        "name": name,
        "email": email,
        "age": age
    }

    # Zapisujemy w "bazie danych"
    users_db[user_id] = user

    return user


# Pobieranie użytkownika po ID
@service(
    http={
        "path": "/api/users/{user_id}",
        "method": "GET"
    },
    mqtt={"topic": "users/get"},
    websocket={"event": "user.get"},
    graphql={"field_name": "user"}
)
def get_user(user_id: str) -> Optional[Dict]:
    """Pobiera użytkownika po ID."""
    if user_id not in users_db:
        return None

    return users_db[user_id]


# Pobieranie listy użytkowników
@service(
    http={
        "path": "/api/users",
        "method": "GET"
    },
    mqtt={"topic": "users/list"},
    websocket={"event": "user.list"},
    graphql={"field_name": "users"}
)
def list_users(limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[Dict]:
    """Pobiera listę użytkowników z opcjonalną paginacją."""
    # Pobieramy listę użytkowników
    users_list = list(users_db.values())

    # Stosujemy paginację
    return users_list[offset:offset + limit]

