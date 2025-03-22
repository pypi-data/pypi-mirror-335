"""
Calculator example demonstrating multiple protocols with pifunc.
"""
import os
from typing import Dict, Union
from pifunc import service, run_services

@service(protocols=["http"], http={"path": "/calculator", "method": "GET"})
def serve_calculator() -> Dict[str, Union[str, bytes]]:
    """Serve the calculator HTML interface."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_path = os.path.join(current_dir, "static", "index.html")
    
    with open(html_path, 'rb') as f:
        content = f.read()
    
    return {
        "content": content,
        "content_type": "text/html"
    }

@service(protocols=["http"], http={"path": "/api/calculator/add", "method": "POST"})
def add_http(a: float, b: float) -> Dict[str, float]:
    """Add two numbers via HTTP."""
    return {"result": a + b}

@service(protocols=["websocket"], websocket={"event": "calculator.add"})
def add_websocket(a: float, b: float) -> float:
    """Add two numbers via WebSocket."""
    return a + b

@service(protocols=["http", "websocket"],
         http={"path": "/api/calculator/multiply", "method": "POST"},
         websocket={"event": "calculator.multiply"})
def multiply(a: float, b: float) -> float:
    """Multiply two numbers - available via both HTTP and WebSocket."""
    return a * b

@service(protocols=["http", "websocket"],
         http={"path": "/api/calculator/divide", "method": "POST"},
         websocket={"event": "calculator.divide"})
def divide(a: float, b: float) -> float:
    """Divide two numbers - available via both HTTP and WebSocket."""
    if b == 0:
        raise ValueError("Division by zero is not allowed")
    return a / b

@service(protocols=["http", "websocket"],
         http={"path": "/api/calculator/subtract", "method": "POST"},
         websocket={"event": "calculator.subtract"})
def subtract(a: float, b: float) -> float:
    """Subtract two numbers - available via both HTTP and WebSocket."""
    return a - b

if __name__ == "__main__":
    http_port = int(os.environ.get("PIFUNC_HTTP_PORT", 8002))
    ws_port = int(os.environ.get("PIFUNC_WS_PORT", 8082))
    
    run_services(
        http={"port": http_port},
        websocket={"port": ws_port}
    )
