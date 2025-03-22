import pytest
import pytest_asyncio
import asyncio
import json
import requests
import paho.mqtt.client as mqtt
from pifunc import service
from pifunc.adapters.http_adapter import HTTPAdapter
from pifunc.adapters.mqtt_adapter import MQTTAdapter
from dataclasses import dataclass
from typing import Dict, List
import websockets
from unittest.mock import MagicMock, patch
import time
from contextlib import asynccontextmanager
import socket
import logging

logger = logging.getLogger(__name__)

def get_free_port():
    """Get a free port number."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port

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
def create_product(product: dict) -> dict:  # Changed from Dict to dict
    return {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "in_stock": product.get("in_stock", True)
    }

@service(
    http={"path": "/api/products/{product_id}", "method": "GET"},
    mqtt={"topic": "products/get"},
    websocket={"event": "product.get"}
)
def get_product(product_id: str) -> dict:  # Changed from Dict to dict
    # Mock database response
    return {
        "id": product_id,
        "name": "Test Product",
        "price": 99.99,
        "in_stock": True
    }

class TestServiceRunner:
    def __init__(self):
        self.ports = {
            "http": get_free_port(),
            "mqtt": get_free_port(),
            "websocket": get_free_port()
        }
        self.http_adapter = HTTPAdapter()
        self.mqtt_adapter = MQTTAdapter()
        self._started = False
        
    async def setup(self):
        if self._started:
            return self.ports
            
        # Configure adapters
        self.http_adapter.setup({
            "port": self.ports["http"],
            "host": "localhost"
        })
        self.mqtt_adapter.setup({
            "port": self.ports["mqtt"],
            "host": "localhost"
        })
        
        # Register services
        for func in [create_product, get_product]:
            metadata = getattr(func, '_pifunc_service', {})
            if "http" in metadata:
                self.http_adapter.register_function(func, metadata)
            if "mqtt" in metadata:
                self.mqtt_adapter.register_function(func, metadata)
                
        # Start adapters
        self.http_adapter.start()
        self.mqtt_adapter.start()
        
        # Wait for services to be ready
        await asyncio.sleep(1)
        self._started = True
        return self.ports
        
    def cleanup(self):
        if self._started:
            self.http_adapter.stop()
            self.mqtt_adapter.stop()
            self._started = False

# Fixtures
@pytest_asyncio.fixture(scope="module")
async def mock_mqtt():
    with patch('paho.mqtt.client.Client') as mock_client:
        client = MagicMock()
        mock_client.return_value = client
        
        # Mock successful connection
        client.connect.return_value = 0
        client.loop_start.return_value = None
        client.loop_stop.return_value = None
        
        # Store messages and handlers
        client.messages = []
        client.handlers = {}
        
        def mock_subscribe(topic, qos=0):
            client.handlers[topic] = None
            return (0, 0)
        
        def mock_publish(topic, payload, qos=0):
            client.messages.append((topic, payload))
            if topic in client.handlers and client.handlers[topic]:
                msg = MagicMock()
                msg.topic = topic
                msg.payload = payload
                client.handlers[topic](client, None, msg)
            return MagicMock()
            
        client.subscribe = mock_subscribe
        client.publish = mock_publish
        
        yield client

@pytest_asyncio.fixture(scope="module")
async def test_service(mock_mqtt):
    runner = TestServiceRunner()
    with patch('pifunc.adapters.mqtt_adapter.mqtt.Client', return_value=mock_mqtt):
        ports = await runner.setup()
        yield ports
        runner.cleanup()

@pytest.fixture
def http_client():
    session = requests.Session()
    return session

# HTTP Integration Tests
@pytest.mark.asyncio
async def test_http_create_product(test_service, http_client):
    """Test creating a product via HTTP"""
    product_data = {
        "id": "prod-1",
        "name": "Test Product",
        "price": 99.99,
        "in_stock": True
    }
    
    # Add debug logging
    logger.info(f"Sending HTTP request to create product: {product_data}")
    
    response = http_client.post(
        f"http://localhost:{test_service['http']}/api/products",
        json={"product": product_data}
    )
    
    # Add debug logging
    logger.info(f"Received HTTP response: {response.text}")
    
    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert "result" in result
    result_data = result["result"]
    assert result_data["id"] == product_data["id"]
    assert result_data["name"] == product_data["name"]
    assert result_data["price"] == product_data["price"]

@pytest.mark.asyncio
async def test_http_get_product(test_service, http_client):
    """Test getting a product via HTTP"""
    product_id = "prod-1"
    response = http_client.get(
        f"http://localhost:{test_service['http']}/api/products/{product_id}"
    )
    
    assert response.status_code == 200, f"Error: {response.text}"
    result = response.json()
    assert "result" in result
    result_data = result["result"]
    assert result_data["id"] == product_id
    assert "name" in result_data
    assert "price" in result_data

@pytest.mark.asyncio
async def test_mqtt_create_product(test_service, mock_mqtt):
    """Test creating a product via MQTT"""
    product_data = {
        "id": "prod-2",
        "name": "MQTT Product",
        "price": 79.99,
        "in_stock": True
    }
    
    # Clear previous messages
    mock_mqtt.messages = []
    
    # Set up response handler
    response_received = asyncio.Event()
    response_data = None
    
    def on_response(client, userdata, msg):
        nonlocal response_data
        try:
            response_data = json.loads(msg.payload)
            response_received.set()
        except Exception as e:
            logger.error(f"Error in MQTT response handler: {e}")
    
    mock_mqtt.handlers["products/create/response"] = on_response
    
    # Add debug logging
    logger.info(f"Sending MQTT message: {product_data}")
    
    # Simulate MQTT message
    mock_mqtt.on_message(None, None, MagicMock(
        topic="products/create",
        payload=json.dumps({"product": product_data}).encode()
    ))
    
    # Wait for response with timeout
    try:
        await asyncio.wait_for(response_received.wait(), timeout=1.0)
    except asyncio.TimeoutError:
        # Add debug logging
        logger.error("MQTT response timeout. Messages received:", mock_mqtt.messages)
        pytest.fail("Timeout waiting for MQTT response")
    
    assert response_data is not None
    assert "result" in response_data
    result = response_data["result"]
    assert result["id"] == product_data["id"]
    assert result["name"] == product_data["name"]
    assert result["price"] == product_data["price"]
