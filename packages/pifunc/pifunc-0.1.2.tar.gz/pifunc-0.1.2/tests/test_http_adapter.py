import pytest
from pifunc.adapters.http_adapter import HTTPAdapter
from dataclasses import dataclass
from typing import Dict, Optional
import json

@pytest.fixture
def http_adapter():
    return HTTPAdapter(port=8080)

def test_adapter_initialization(http_adapter):
    """Test HTTP adapter initialization"""
    assert http_adapter.port == 8080
    assert http_adapter.host == 'localhost'

def test_route_registration(http_adapter):
    """Test registering a route with the adapter"""
    def test_handler(a: int, b: int) -> int:
        return a + b

    http_adapter.register_route(
        path='/api/add',
        method='POST',
        handler=test_handler
    )

    assert '/api/add' in http_adapter.routes
    assert http_adapter.routes['/api/add']['method'] == 'POST'
    assert http_adapter.routes['/api/add']['handler'] == test_handler

def test_path_parameter_parsing(http_adapter):
    """Test parsing path parameters from URLs"""
    def get_user(user_id: str) -> Dict:
        return {"id": user_id, "name": "Test User"}

    http_adapter.register_route(
        path='/api/users/{user_id}',
        method='GET',
        handler=get_user
    )

    params = http_adapter._extract_path_params('/api/users/{user_id}', '/api/users/123')
    assert params == {'user_id': '123'}

def test_query_parameter_parsing(http_adapter):
    """Test parsing query parameters"""
    query_string = 'page=1&limit=10&sort=desc'
    params = http_adapter._parse_query_params(query_string)
    
    assert params == {
        'page': '1',
        'limit': '10',
        'sort': 'desc'
    }

def test_request_body_parsing(http_adapter):
    """Test parsing JSON request body"""
    @dataclass
    class UserData:
        name: str
        age: int
        email: Optional[str] = None

    def create_user(data: UserData) -> Dict:
        return {
            "name": data.name,
            "age": data.age,
            "email": data.email
        }

    http_adapter.register_route(
        path='/api/users',
        method='POST',
        handler=create_user
    )

    request_body = {
        "name": "John Doe",
        "age": 30,
        "email": "john@example.com"
    }

    parsed_data = http_adapter._parse_request_body(
        json.dumps(request_body),
        UserData
    )

    assert isinstance(parsed_data, UserData)
    assert parsed_data.name == "John Doe"
    assert parsed_data.age == 30
    assert parsed_data.email == "john@example.com"

def test_response_formatting(http_adapter):
    """Test formatting response data"""
    response_data = {
        "id": 123,
        "name": "Test Product",
        "price": 99.99
    }

    formatted_response = http_adapter._format_response(response_data)
    assert isinstance(formatted_response, str)
    
    parsed_response = json.loads(formatted_response)
    assert parsed_response == response_data

def test_error_handling(http_adapter):
    """Test error handling in HTTP adapter"""
    def failing_handler():
        raise ValueError("Test error")

    http_adapter.register_route(
        path='/api/error',
        method='GET',
        handler=failing_handler
    )

    with pytest.raises(ValueError) as exc:
        failing_handler()
    assert str(exc.value) == "Test error"

def test_middleware_execution(http_adapter):
    """Test middleware execution in request processing"""
    def auth_middleware(handler):
        def wrapper(*args, **kwargs):
            # Simulate auth check
            if 'authorized' not in kwargs:
                raise ValueError("Unauthorized")
            return handler(*args, **kwargs)
        return wrapper

    def test_handler(authorized: bool = False) -> str:
        return "Success"

    http_adapter.register_route(
        path='/api/secure',
        method='GET',
        handler=test_handler,
        middleware=[auth_middleware]
    )

    # Test unauthorized access
    with pytest.raises(ValueError) as exc:
        test_handler()
    assert str(exc.value) == "Unauthorized"

    # Test authorized access
    result = test_handler(authorized=True)
    assert result == "Success"

def test_content_type_handling(http_adapter):
    """Test handling different content types"""
    def handler(data: Dict) -> Dict:
        return data

    http_adapter.register_route(
        path='/api/echo',
        method='POST',
        handler=handler
    )

    # Test JSON content
    json_data = {"test": "value"}
    parsed_data = http_adapter._parse_request_body(
        json.dumps(json_data),
        Dict
    )
    assert parsed_data == json_data

def test_cors_headers(http_adapter):
    """Test CORS headers in responses"""
    cors_headers = http_adapter._get_cors_headers()
    
    assert 'Access-Control-Allow-Origin' in cors_headers
    assert 'Access-Control-Allow-Methods' in cors_headers
    assert 'Access-Control-Allow-Headers' in cors_headers
