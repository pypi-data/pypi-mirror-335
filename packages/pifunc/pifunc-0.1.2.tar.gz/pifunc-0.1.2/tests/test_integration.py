import pytest
import asyncio
import json
import requests
import paho.mqtt.client as mqtt
from pifunc import service, run_services
from dataclasses import dataclass
from typing import Dict, List
import websockets

# Test service definitions
@dataclass
class Product:
    id: str
    name: str
    price: float
    in_stock: bool = True

@service(
    http={"path": "/api/products", "method": "POST"},
    mqtt={"topic": "products/create"},
    websocket={"event": "product.create"}
)
def create_product(product: Product) -> Dict:
    return {
        "id": product.id,
        "name": product.name,
        "price": product.price,
        "in_stock": product.in_stock
    }

@service(
    http={"path": "/api/products/{product_id}", "method": "GET"},
    mqtt={"topic": "products/get"},
    websocket={"event": "product.get"}
)
def get_product(product_id: str) -> Dict:
    # Mock database response
    return {
        "id": product_id,
        "name": "Test Product",
        "price": 99.99,
        "in_stock": True
    }

@service(
    http={"path": "/api/stream", "method": "GET"},
    websocket={"event": "stream.data"}
)
async def stream_data(count: int = 3) -> List[Dict]:
    """Stream a sequence of data items"""
    results = []
    for i in range(count):
        results.append({"item": i, "timestamp": f"2025-03-19T{14+i}:00:00Z"})
        await asyncio.sleep(0.1)
    return results

# Fixtures
@pytest.fixture(scope="module")
def service_ports():
    return {
        "http": 8080,
        "mqtt": 1883,
        "websocket": 8765
    }

@pytest.fixture(scope="module")
def run_test_service(service_ports):
    # Start the service in a separate process
    process = run_services(
        http={"port": service_ports["http"]},
        mqtt={"port": service_ports["mqtt"]},
        websocket={"port": service_ports["websocket"]}
    )
    yield service_ports
    process.terminate()

@pytest.fixture
def http_client():
    return requests.Session()

@pytest.fixture
def mqtt_client(service_ports):
    client = mqtt.Client()
    client.connect("localhost", service_ports["mqtt"])
    client.loop_start()
    yield client
    client.loop_stop()
    client.disconnect()

# HTTP Integration Tests
def test_http_create_product(run_test_service, http_client):
    """Test creating a product via HTTP"""
    product_data = {
        "id": "prod-1",
        "name": "Test Product",
        "price": 99.99,
        "in_stock": True
    }
    
    response = http_client.post(
        f"http://localhost:{run_test_service['http']}/api/products",
        json=product_data
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == product_data["id"]
    assert result["name"] == product_data["name"]
    assert result["price"] == product_data["price"]

def test_http_get_product(run_test_service, http_client):
    """Test getting a product via HTTP"""
    product_id = "prod-1"
    response = http_client.get(
        f"http://localhost:{run_test_service['http']}/api/products/{product_id}"
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == product_id
    assert "name" in result
    assert "price" in result

# MQTT Integration Tests
def test_mqtt_create_product(run_test_service, mqtt_client):
    """Test creating a product via MQTT"""
    result = None
    
    def on_message(client, userdata, msg):
        nonlocal result
        result = json.loads(msg.payload)
    
    mqtt_client.subscribe("products/create/response")
    mqtt_client.on_message = on_message
    
    product_data = {
        "id": "prod-2",
        "name": "MQTT Product",
        "price": 79.99,
        "in_stock": True
    }
    
    mqtt_client.publish("products/create", json.dumps(product_data))
    
    # Wait for response
    for _ in range(10):
        if result is not None:
            break
        asyncio.sleep(0.1)
    
    assert result is not None
    assert result["id"] == product_data["id"]
    assert result["name"] == product_data["name"]
    assert result["price"] == product_data["price"]

# WebSocket Integration Tests
@pytest.mark.asyncio
async def test_websocket_create_product(run_test_service):
    """Test creating a product via WebSocket"""
    async with websockets.connect(
        f"ws://localhost:{run_test_service['websocket']}"
    ) as websocket:
        product_data = {
            "id": "prod-3",
            "name": "WebSocket Product",
            "price": 149.99,
            "in_stock": True
        }
        
        await websocket.send(json.dumps({
            "event": "product.create",
            "data": product_data
        }))
        
        response = await websocket.recv()
        result = json.loads(response)
        
        assert result["id"] == product_data["id"]
        assert result["name"] == product_data["name"]
        assert result["price"] == product_data["price"]

@pytest.mark.asyncio
async def test_websocket_stream_data(run_test_service):
    """Test streaming data via WebSocket"""
    async with websockets.connect(
        f"ws://localhost:{run_test_service['websocket']}"
    ) as websocket:
        await websocket.send(json.dumps({
            "event": "stream.data",
            "data": {"count": 3}
        }))
        
        results = []
        for _ in range(3):
            response = await websocket.recv()
            results.append(json.loads(response))
        
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result["item"] == i
            assert "timestamp" in result

# Cross-Protocol Integration Tests
def test_cross_protocol_product_creation(run_test_service, http_client, mqtt_client):
    """Test creating and retrieving products across different protocols"""
    # Create via HTTP
    http_product = {
        "id": "cross-1",
        "name": "Cross-Protocol Product",
        "price": 199.99,
        "in_stock": True
    }
    
    http_response = http_client.post(
        f"http://localhost:{run_test_service['http']}/api/products",
        json=http_product
    )
    assert http_response.status_code == 200
    
    # Retrieve via MQTT
    mqtt_result = None
    def on_message(client, userdata, msg):
        nonlocal mqtt_result
        mqtt_result = json.loads(msg.payload)
    
    mqtt_client.subscribe("products/get/response")
    mqtt_client.on_message = on_message
    mqtt_client.publish("products/get", json.dumps({"product_id": "cross-1"}))
    
    # Wait for response
    for _ in range(10):
        if mqtt_result is not None:
            break
        asyncio.sleep(0.1)
    
    assert mqtt_result is not None
    assert mqtt_result["id"] == http_product["id"]
    assert mqtt_result["name"] == http_product["name"]
