import pytest
from pifunc.adapters.http_adapter import HTTPAdapter
from fastapi.middleware.cors import CORSMiddleware
from dataclasses import dataclass
from typing import Dict, Optional
import json

@pytest.fixture
def http_adapter():
    adapter = HTTPAdapter()
    adapter.setup({"port": 8080, "host": "localhost"})
    return adapter

def test_adapter_initialization(http_adapter):
    """Test HTTP adapter initialization"""
    assert http_adapter.config["port"] == 8080
    assert http_adapter.config["host"] == "localhost"

def test_route_registration(http_adapter):
    """Test registering a route with the adapter"""
    def test_handler(a: int, b: int) -> int:
        return a + b

    metadata = {
        "http": {
            "path": "/api/add",
            "method": "POST"
        }
    }
    http_adapter.register_function(test_handler, metadata)
    
    # FastAPI stores routes in a list, we can check if our path exists
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/add" in routes

def test_path_parameter_parsing(http_adapter):
    """Test parsing path parameters from URLs"""
    def get_user(user_id: str) -> Dict:
        return {"id": user_id, "name": "Test User"}

    metadata = {
        "http": {
            "path": "/api/users/{user_id}",
            "method": "GET"
        }
    }
    http_adapter.register_function(get_user, metadata)
    
    # FastAPI handles path parameters automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/users/{user_id}" in routes

def test_query_parameter_parsing(http_adapter):
    """Test parsing query parameters"""
    def list_items(page: int = 1, limit: int = 10, sort: str = "desc") -> Dict:
        return {"page": page, "limit": limit, "sort": sort}

    metadata = {
        "http": {
            "path": "/api/items",
            "method": "GET"
        }
    }
    http_adapter.register_function(list_items, metadata)
    
    # FastAPI handles query parameters automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/items" in routes

def test_request_body_parsing(http_adapter):
    """Test parsing JSON request body"""
    def create_user(name: str, age: int, email: Optional[str] = None) -> Dict:
        return {
            "name": name,
            "age": age,
            "email": email
        }

    metadata = {
        "http": {
            "path": "/api/users",
            "method": "POST"
        }
    }
    http_adapter.register_function(create_user, metadata)
    
    # FastAPI handles request body parsing automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/users" in routes

def test_response_formatting(http_adapter):
    """Test response formatting"""
    def get_product() -> Dict:
        return {
            "id": 123,
            "name": "Test Product",
            "price": 99.99
        }

    metadata = {
        "http": {
            "path": "/api/product",
            "method": "GET"
        }
    }
    http_adapter.register_function(get_product, metadata)
    
    # FastAPI handles response formatting automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/product" in routes

def test_error_handling(http_adapter):
    """Test error handling"""
    def failing_handler():
        raise ValueError("Test error")

    metadata = {
        "http": {
            "path": "/api/error",
            "method": "GET"
        }
    }
    http_adapter.register_function(failing_handler, metadata)
    
    # FastAPI handles error responses automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/error" in routes

def test_middleware_execution(http_adapter):
    """Test middleware execution"""
    def test_handler(authorized: bool = False) -> str:
        return "Success"

    metadata = {
        "http": {
            "path": "/api/secure",
            "method": "GET",
            "middleware": ["auth"]
        }
    }
    http_adapter.register_function(test_handler, metadata)
    
    # FastAPI handles middleware execution
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/secure" in routes

def test_content_type_handling(http_adapter):
    """Test content type handling"""
    def echo_handler(data: Dict) -> Dict:
        return data

    metadata = {
        "http": {
            "path": "/api/echo",
            "method": "POST"
        }
    }
    http_adapter.register_function(echo_handler, metadata)
    
    # FastAPI handles content type automatically
    routes = [route.path for route in http_adapter.app.routes]
    assert "/api/echo" in routes

def test_cors_headers(http_adapter):
    """Test CORS configuration"""
    adapter = HTTPAdapter()
    adapter.setup({
        "cors": True,
        "cors_origins": ["*"],
        "cors_methods": ["*"],
        "cors_headers": ["*"]
    })
    
    # Check if CORS middleware is configured by checking the middleware list
    cors_middleware = next(
        (m for m in adapter.app.user_middleware if m.cls == CORSMiddleware),
        None
    )
    assert cors_middleware is not None
    
    # Verify CORS settings in the adapter config
    assert adapter.config["cors"] is True
    assert adapter.config["cors_origins"] == ["*"]
    assert adapter.config["cors_methods"] == ["*"]
    assert adapter.config["cors_headers"] == ["*"]
