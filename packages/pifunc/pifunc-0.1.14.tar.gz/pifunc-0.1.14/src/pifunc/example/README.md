# PiFunc Example Services

This directory contains example services demonstrating various features and protocols supported by PiFunc. Each service showcases different functionalities and can be run independently or together.

## Available Services

### 1. Calculator Service (Port 8000)
- Basic calculator operations (add, subtract, multiply, divide)
- Protocols: HTTP, WebSocket
- Web interface available at http://localhost:8000

### 2. Math Service (Port 8001)
- Advanced mathematical operations
- Protocols: HTTP, WebSocket, MQTT, gRPC
- Functions:
  - Factorial calculation
  - Fibonacci sequence
  - Newton's square root method

### 3. String Service (Port 8002)
- String manipulation operations
- Protocols: HTTP, WebSocket, MQTT, gRPC
- Functions:
  - String reversal
  - Word counting
  - Title case conversion
  - Palindrome checking
  - Substring finding

### 4. Data Structures Service (Port 8003)
- List and dictionary operations
- Protocols: HTTP, WebSocket, MQTT, gRPC
- Functions:
  - List sorting
  - Duplicate removal
  - Dictionary merging
  - List item finding
  - Dictionary filtering

## Protocol Support

Each service demonstrates different protocols:
- HTTP: RESTful API endpoints
- WebSocket: Real-time bidirectional communication
- MQTT: Message queue for publish/subscribe patterns
- gRPC: High-performance RPC framework

## Running the Services

### Individual Services

Each service can be run independently using its own docker-compose file:

```bash
# Run Calculator Service
cd calculator
docker-compose up

# Run Math Service
cd math_service
docker-compose up

# Run String Service
cd string_service
docker-compose up

# Run Data Service
cd data_service
docker-compose up
```

### All Services Together

To run all services together, use the main docker-compose file in the example directory:

```bash
docker-compose up
```

This will start all services and their respective demo clients.

## Service Ports

| Service    | HTTP  | WebSocket | gRPC   |
|------------|-------|-----------|--------|
| Calculator | 8000  | 8080      | -      |
| Math       | 8001  | 8081      | 50051  |
| String     | 8002  | 8082      | 50052  |
| Data       | 8003  | 8083      | 50053  |

Additionally, a shared MQTT broker is available on port 1883 (MQTT) and 9001 (MQTT over WebSocket).

## Demo Clients

Each service comes with a demo client that shows how to:
- Connect using different protocols
- Send requests and handle responses
- Work with various data types and operations

The demo clients are automatically started when using docker-compose, but can also be run manually using Python.

## Testing the Services

1. Start the services using docker-compose
2. Watch the demo clients automatically test different protocols
3. Use the calculator's web interface at http://localhost:8000
4. Try the other services using your preferred protocol client:
   - HTTP: Use curl, Postman, or any HTTP client
   - WebSocket: Use wscat or a WebSocket client
   - MQTT: Use mosquitto_pub/sub or MQTT.js
   - gRPC: Use grpcurl or any gRPC client

This example suite demonstrates the flexibility and power of PiFunc in creating multi-protocol services that can work together in a microservices architecture.
