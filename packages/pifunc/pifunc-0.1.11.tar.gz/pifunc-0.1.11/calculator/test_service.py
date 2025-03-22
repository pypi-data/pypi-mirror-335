import pytest
from service import add_http, add_websocket, multiply, divide, subtract

def test_add_http():
    """Test HTTP addition endpoint"""
    result = add_http(5.0, 3.0)
    assert result == {"result": 8.0}
    
    # Test with negative numbers
    result = add_http(-2.0, 3.0)
    assert result == {"result": 1.0}
    
    # Test with zero
    result = add_http(0.0, 5.0)
    assert result == {"result": 5.0}

def test_add_websocket():
    """Test WebSocket addition endpoint"""
    result = add_websocket(5.0, 3.0)
    assert result == 8.0
    
    # Test with negative numbers
    result = add_websocket(-2.0, 3.0)
    assert result == 1.0
    
    # Test with zero
    result = add_websocket(0.0, 5.0)
    assert result == 5.0

def test_multiply():
    """Test multiplication endpoint"""
    result = multiply(4.0, 3.0)
    assert result == 12.0
    
    # Test with zero
    result = multiply(5.0, 0.0)
    assert result == 0.0
    
    # Test with negative numbers
    result = multiply(-2.0, 3.0)
    assert result == -6.0
    
    # Test with two negative numbers
    result = multiply(-2.0, -3.0)
    assert result == 6.0

def test_divide():
    """Test division endpoint"""
    result = divide(6.0, 2.0)
    assert result == 3.0
    
    # Test with negative numbers
    result = divide(-6.0, 2.0)
    assert result == -3.0
    
    # Test division by 1
    result = divide(5.0, 1.0)
    assert result == 5.0
    
    # Test division by zero should raise ValueError
    with pytest.raises(ValueError) as exc_info:
        divide(5.0, 0.0)
    assert str(exc_info.value) == "Division by zero is not allowed"

def test_subtract():
    """Test subtraction endpoint"""
    result = subtract(5.0, 3.0)
    assert result == 2.0
    
    # Test with negative numbers
    result = subtract(-2.0, 3.0)
    assert result == -5.0
    
    # Test with zero
    result = subtract(5.0, 0.0)
    assert result == 5.0
    
    # Test subtracting from zero
    result = subtract(0.0, 5.0)
    assert result == -5.0
