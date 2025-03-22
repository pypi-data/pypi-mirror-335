# PI func -> Protocol Interface Functions

PIfunc revolutionizes how you build networked applications by letting you **write your function once** and expose it via **multiple communication protocols simultaneously**. No duplicate code. No inconsistencies. Just clean, maintainable, protocol-agnostic code.

<div align="center">
  <h3>One function, every protocol. Everywhere.</h3>
</div>

## 🚀 Installation

```bash
pip install pifunc
```

## 📚 Quick Start

```python
from pifunc import service, run_services

@service(
    http={"path": "/api/add", "method": "POST"},
    websocket={"event": "math.add"},
    grpc={}
)
def add(a: int, b: int) -> int:
    """Add two numbers together."""
    return a + b

if __name__ == "__main__":
    run_services(
        http={"port": 8080},
        websocket={"port": 8081},
        grpc={"port": 50051},
        watch=True  # Auto-reload on code changes
    )
```

Now your function is accessible via:
- HTTP: `POST /api/add` with JSON body `{"a": 5, "b": 3}`
- WebSocket: Send event `math.add` with payload `{"a": 5, "b": 3}`
- gRPC: Call the `add` method with parameters `a=5, b=3`

## 🔌 Supported Protocols

| Protocol | Description | Best For |
|----------|-------------|----------|
| **HTTP/REST** | RESTful API with JSON | Web clients, general API access |
| **gRPC** | High-performance RPC | Microservices, performance-critical systems |
| **MQTT** | Lightweight pub/sub | IoT devices, mobile apps |
| **WebSocket** | Bidirectional comms | Real-time applications, chat |
| **GraphQL** | Query language | Flexible data requirements |
| **ZeroMQ** | Distributed messaging | High-throughput, low-latency systems |
| **AMQP** | Advanced Message Queuing | Enterprise messaging, reliable delivery |
| **Redis** | In-memory data structure | Caching, pub/sub, messaging |
| **CRON** | Scheduled tasks | Periodic jobs, background tasks |

## ✨ Features

- **Multi-Protocol Support**: Expose functions via multiple protocols at once
- **Zero Boilerplate**: Single decorator approach with sensible defaults
- **Type Safety**: Automatic type validation and conversion
- **Hot Reload**: Instant updates during development
- **Protocol-Specific Configurations**: Fine-tune each protocol interface
- **Automatic Documentation**: OpenAPI, gRPC reflection, and GraphQL introspection
- **Client Integration**: Built-in client with `@client` decorator for inter-service communication
- **Scheduled Tasks**: CRON-like scheduling with `cron` protocol
- **Serverless Deployment**: Support for AWS Lambda, Google Cloud Functions, and Azure Functions
- **Comprehensive CLI**: Manage and test your services with ease
- **Monitoring & Health Checks**: Built-in observability
- **Enterprise-Ready**: Authentication, authorization, and middleware support

## 📚 Examples

### Parameter Handling

```python
@service(
    http={"path": "/api/products", "method": "POST"},
    mqtt={"topic": "products/create"}
)
def create_product(product: dict) -> dict:
    """Create a new product.
    
    Note: When working with dictionary parameters, use `dict` instead of `Dict`
    for better type handling across protocols.
    """
    return {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "in_stock": product.get("in_stock", True)
    }
```

### Client-Server Pattern

```python
from pifunc import service, client, run_services
import random

# Server-side service
@service(
    http={"path": "/api/products", "method": "POST"}
)
def create_product(product: dict) -> dict:
    """Create a new product."""
    return {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "created": True
    }

# Client-side function with scheduled execution
@client(
    http={"path": "/api/products", "method": "POST"}
)
@service(
    cron={"interval": "1h"}  # Run every hour
)
def generate_product() -> dict:
    """Generate a random product and send it to the create_product service."""
    return {
        "id": f"PROD-{random.randint(1000, 9999)}",
        "name": f"Automated Product {random.randint(1, 100)}",
        "price": round(random.uniform(10.0, 100.0), 2)
    }

if __name__ == "__main__":
    run_services(
        http={"port": 8080},
        cron={"check_interval": 1},
        watch=True
    )
```

### Serverless Functions

```python
from pifunc import service

@service(
    lambda={"memory": 128, "timeout": 30},
    http={"path": "/api/process", "method": "POST"}
)
def process_data(data: dict) -> dict:
    """Process data in AWS Lambda or locally via HTTP."""
    result = perform_calculation(data)
    return {"result": result, "processed": True}
```

### Advanced Configuration

```python
@service(
    # HTTP configuration
    http={
        "path": "/api/users/{user_id}",
        "method": "GET",
        "middleware": [auth_middleware, logging_middleware]
    },
    # MQTT configuration
    mqtt={
        "topic": "users/get",
        "qos": 1,
        "retain": False
    },
    # WebSocket configuration
    websocket={
        "event": "user.get",
        "namespace": "/users"
    },
    # GraphQL configuration
    graphql={
        "field_name": "user",
        "description": "Get user by ID"
    }
)
def get_user(user_id: str) -> dict:
    """Get user details by ID."""
    return db.get_user(user_id)
```

## 🛠️ CLI Usage

```bash
# Start a service
python your_service.py

# Call a function via HTTP (default protocol)
pifunc call add --args '{"a": 5, "b": 3}'

# Call a function with specific protocol
pifunc call add --protocol grpc --args '{"a": 5, "b": 3}'

# Generate client code
pifunc generate client --language python --output client.py

# View service documentation
pifunc docs serve
```

## 📖 Documentation

Comprehensive documentation is available at [https://www.pifunc.com/docs](https://www.pifunc.com/docs)

- [API Reference](https://www.pifunc.com/docs/api-reference)
- [Protocol Configurations](https://www.pifunc.com/docs/protocols)
- [Advanced Usage](https://www.pifunc.com/docs/advanced)
- [Deployment Guide](https://www.pifunc.com/docs/deployment)
- [Extending PIfunc](https://www.pifunc.com/docs/extending)

## 🧪 Testing

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run all tests
pytest

# Run specific test categories
pytest tests/test_http_adapter.py
pytest tests/test_integration.py
```

## 🤝 Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get started.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

PIfunc is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.

---

<div align="center">
  <p>Built with ❤️ by the PIfunc team and contributors</p>
  <p>
    <a href="https://www.pifunc.com">Website</a> •
    <a href="https://twitter.com/pifunc">Twitter</a> •
    <a href="https://discord.gg/pifunc">Discord</a>
  </p>
</div>