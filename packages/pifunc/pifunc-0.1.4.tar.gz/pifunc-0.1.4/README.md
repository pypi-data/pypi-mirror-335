# PI func -> Protocol Interface Functions

[Previous content up to the Examples section remains unchanged...]

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

# Call via HTTP:
# POST /api/products
# {"product": {"id": "123", "name": "Widget", "price": 99.99}}

# Call via MQTT:
# Topic: products/create
# Payload: {"product": {"id": "123", "name": "Widget", "price": 99.99}}
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
def get_user(user_id: str) -> dict:  # Use dict instead of Dict
    """Get user details by ID."""
    return db.get_user(user_id)
```

### Debugging and Logging

PIfunc provides detailed logging for both HTTP and MQTT adapters to help with debugging:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

@service(
    http={"path": "/api/data", "method": "POST"},
    mqtt={"topic": "data/process"}
)
def process_data(data: dict) -> dict:
    """Process data with detailed logging."""
    return {"processed": data}

# Logs will show:
# - Incoming request/message details
# - Parameter conversion steps
# - Function execution details
# - Response/publication details
# - Any errors or issues that occur
```

[Rest of the content remains unchanged...]
