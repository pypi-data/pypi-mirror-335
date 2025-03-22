from pifunc import service, run_services
from typing import Dict

@service(
    http={"path": "/api/calculator/add", "method": "POST"},
    mqtt={"topic": "calculator/add"},
    websocket={"event": "calculator.add"}
)
def add(a: int, b: int) -> dict:
    """Add two numbers."""
    return {"result": a + b}

@service(
    http={"path": "/api/calculator/subtract", "method": "POST"},
    mqtt={"topic": "calculator/subtract"},
    websocket={"event": "calculator.subtract"}
)
def subtract(a: int, b: int) -> dict:
    """Subtract b from a."""
    return {"result": a - b}

@service(
    http={"path": "/api/calculator/multiply", "method": "POST"},
    mqtt={"topic": "calculator/multiply"},
    websocket={"event": "calculator.multiply"}
)
def multiply(a: int, b: int) -> dict:
    """Multiply two numbers."""
    return {"result": a * b}

@service(
    http={"path": "/api/calculator/divide", "method": "POST"},
    mqtt={"topic": "calculator/divide"},
    websocket={"event": "calculator.divide"}
)
def divide(a: float, b: float) -> dict:
    """Divide a by b."""
    if b == 0:
        return {"error": "Division by zero"}
    return {"result": a / b}

if __name__ == "__main__":
    run_services(
        http={"port": 8080},
        mqtt={"port": 1883},
        websocket={"port": 8765}
    )
