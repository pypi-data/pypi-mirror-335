import pytest
from pifunc import service, run_services
from dataclasses import dataclass
from typing import Dict

def test_basic_service_decorator():
    """Test basic service decorator without protocol configs"""
    @service()
    def add(a: int, b: int) -> int:
        return a + b
    
    assert hasattr(add, '_pifunc_service')
    assert add(2, 3) == 5

def test_service_with_http_config():
    """Test service decorator with HTTP configuration"""
    @service(
        http={
            "path": "/api/calculator/add",
            "method": "POST"
        }
    )
    def add(a: int, b: int) -> int:
        return a + b
    
    config = getattr(add, '_pifunc_service')
    assert config['http']['path'] == '/api/calculator/add'
    assert config['http']['method'] == 'POST'
    assert add(2, 3) == 5

def test_service_with_mqtt_config():
    """Test service decorator with MQTT configuration"""
    @service(
        mqtt={
            "topic": "calculator/add",
            "qos": 1
        }
    )
    def add(a: int, b: int) -> int:
        return a + b
    
    config = getattr(add, '_pifunc_service')
    assert config['mqtt']['topic'] == 'calculator/add'
    assert config['mqtt']['qos'] == 1
    assert add(2, 3) == 5

def test_service_with_websocket_config():
    """Test service decorator with WebSocket configuration"""
    @service(
        websocket={
            "event": "calculator.add"
        }
    )
    def add(a: int, b: int) -> int:
        return a + b
    
    config = getattr(add, '_pifunc_service')
    assert config['websocket']['event'] == 'calculator.add'
    assert add(2, 3) == 5

def test_service_with_multiple_protocols():
    """Test service decorator with multiple protocol configurations"""
    @service(
        http={"path": "/api/add", "method": "POST"},
        mqtt={"topic": "calculator/add"},
        websocket={"event": "calculator.add"}
    )
    def add(a: int, b: int) -> int:
        return a + b
    
    config = getattr(add, '_pifunc_service')
    assert config['http']['path'] == '/api/add'
    assert config['mqtt']['topic'] == 'calculator/add'
    assert config['websocket']['event'] == 'calculator.add'
    assert add(2, 3) == 5

def test_service_with_complex_types():
    """Test service decorator with complex data types"""
    @dataclass
    class Product:
        id: str
        name: str
        price: float
        
    @service(
        http={"path": "/api/products", "method": "POST"}
    )
    def create_product(product: Product) -> Dict:
        return {
            "id": product.id,
            "name": product.name,
            "price": product.price
        }
    
    product = Product(id="123", name="Test Product", price=99.99)
    result = create_product(product)
    assert result["id"] == "123"
    assert result["name"] == "Test Product"
    assert result["price"] == 99.99

def test_service_with_invalid_config():
    """Test service decorator with invalid configuration"""
    with pytest.raises(ValueError):
        @service(
            http={"invalid_key": "value"}
        )
        def add(a: int, b: int) -> int:
            return a + b

def test_service_with_async_function():
    """Test service decorator with async function"""
    import asyncio
    
    @service(
        http={"path": "/api/async", "method": "GET"}
    )
    async def async_function():
        await asyncio.sleep(0.1)
        return "async result"
    
    config = getattr(async_function, '_pifunc_service')
    assert config['http']['path'] == '/api/async'
    
    # Run async function
    result = asyncio.run(async_function())
    assert result == "async result"

def test_service_with_middleware():
    """Test service decorator with middleware configuration"""
    def test_middleware(func):
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        return wrapper
    
    @service(
        http={
            "path": "/api/secure",
            "method": "POST",
            "middleware": [test_middleware]
        }
    )
    def secure_function(data: str) -> str:
        return f"processed: {data}"
    
    config = getattr(secure_function, '_pifunc_service')
    assert len(config['http']['middleware']) == 1
    assert secure_function("test") == "processed: test"
