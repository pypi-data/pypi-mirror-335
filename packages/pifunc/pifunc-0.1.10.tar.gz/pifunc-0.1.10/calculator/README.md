# PiFunc Calculator Example

This example demonstrates how to use PiFunc to create a multi-protocol calculator service. It includes:
- Web-based calculator interface
- Multiple protocol support (HTTP, WebSocket, Redis, MQTT)
- Example client implementations
- Docker Compose setup for easy deployment

## Project Structure

```
calculator/
├── static/
│   └── index.html         # Web interface for the calculator
├── service.py             # Main calculator service implementation
├── client.py             # Example clients using different protocols
├── docker-compose.yml    # Docker services configuration
└── README.md            # This documentation
```

## Features

The calculator service provides:
- Basic arithmetic operations (add, subtract, multiply, divide)
- Multiple protocol support:
  - HTTP REST API
  - WebSocket real-time communication
  - Redis pub/sub integration
  - MQTT messaging


```bash
# Stop all running containers first
docker stop $(docker ps -a -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Prune unused Docker resources
docker system prune -a
```
## Running the Example

1. Start all services using Docker Compose:
   ```bash
   docker-compose up --build
   ```

2. Access the web interface:
   - Open `http://localhost:8000/calculator` in your browser

```bash
docker-compose down --rmi all && docker-compose up --build
```

```bash
cd calculator && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

```bash
python -m venv venv && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt
```

```bash
pkill -f "python service.py"; cd calculator; python service.py
pkill -f "python service.py"
python service.py
```

```bash
python service.py
```

```bash
pytest calculator/test_service.py -v
```

## Available Endpoints

### HTTP Endpoints

- `GET /calculator` - Serves the calculator web interface
- `GET /api/calculator/add?a=<number>&b=<number>` - Add two numbers
- `GET /api/calculator/multiply?a=<number>&b=<number>` - Multiply two numbers
- `GET /api/calculator/divide?a=<number>&b=<number>` - Divide two numbers
- `GET /api/calculator/subtract?a=<number>&b=<number>` - Subtract two numbers

### WebSocket Topics

- `calculator.add` - Add two numbers
- `calculator.multiply` - Multiply two numbers
- `calculator.divide` - Divide two numbers
- `calculator.subtract` - Subtract two numbers

### MQTT Topics

- `calculator/add` - Add operation
- `calculator/result` - Results channel

### Redis Channels

- `calc_channel` - Calculator operations
- `calc_result` - Results channel

## Example Usage

### Using HTTP

```python
from pifunc import http_client

# Add two numbers
result = await http_client.get("http://localhost:8000/api/calculator/add", 
                             params={"a": 5, "b": 3})
print(result)  # {"result": 8}
```

### Using WebSocket

```python
from pifunc import websocket_client

async with websocket_client.connect("ws://localhost:8080") as ws:
    result = await ws.call("calculator.add", 10, 5)
    print(result)  # 15
```

### Using MQTT

```python
from pifunc import mqtt_client

async with mqtt_client.connect("mqtt://localhost:1883") as mqtt:
    await mqtt.publish("calculator/add", {"a": 20, "b": 10})
    result = await mqtt.subscribe("calculator/result")
    print(result)  # 30
```

### Using Redis

```python
from pifunc import redis_client

async with redis_client.connect("redis://localhost:6379") as redis:
    await redis.publish("calc_channel", {"operation": "add", "a": 15, "b": 5})
    result = await redis.subscribe("calc_result")
    print(result)  # 20
```

## Running the Demo Client

The example includes a demo client that showcases all protocols:

```bash
# In a new terminal after starting the services
docker-compose run demo-client
```

This will run demonstrations of all supported protocols, showing how to interact with the calculator service using different communication methods.
