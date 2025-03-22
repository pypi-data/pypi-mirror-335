"""
Example client demonstrating how to use the math service through different protocols.
"""
import asyncio
import json
from pifunc import HttpClient, WebSocketClient, MqttClient, GrpcClient

async def test_http_client():
    """Test HTTP protocol endpoints."""
    client = HttpClient("http://math:8001")
    
    # Test factorial
    result = await client.call("/api/math/factorial", {"n": 5})
    print(f"HTTP - Factorial of 5: {result}")
    
    # Test fibonacci
    result = await client.call("/api/math/fibonacci", {"n": 10})
    print(f"HTTP - 10th Fibonacci number: {result}")
    
    # Test square root
    result = await client.call("/api/math/newton-sqrt", {"n": 16.0})
    print(f"HTTP - Square root of 16: {result}")

async def test_websocket_client():
    """Test WebSocket protocol endpoints."""
    client = WebSocketClient("ws://math:8081")
    await client.connect()
    
    # Test factorial
    result = await client.call("math.factorial", {"n": 6})
    print(f"WebSocket - Factorial of 6: {result}")
    
    # Test fibonacci
    result = await client.call("math.fibonacci", {"n": 11})
    print(f"WebSocket - 11th Fibonacci number: {result}")
    
    # Test square root
    result = await client.call("math.newton-sqrt", {"n": 25.0})
    print(f"WebSocket - Square root of 25: {result}")
    
    await client.disconnect()

async def test_mqtt_client():
    """Test MQTT protocol endpoints."""
    client = MqttClient("mqtt://mqtt-broker:1883")
    await client.connect()
    
    # Test factorial
    result = await client.call("math/factorial", {"n": 7})
    print(f"MQTT - Factorial of 7: {result}")
    
    # Test fibonacci
    result = await client.call("math/fibonacci", {"n": 12})
    print(f"MQTT - 12th Fibonacci number: {result}")
    
    # Test square root
    result = await client.call("math/newton-sqrt", {"n": 36.0})
    print(f"MQTT - Square root of 36: {result}")
    
    await client.disconnect()

async def test_grpc_client():
    """Test gRPC protocol endpoints."""
    client = GrpcClient("grpc://math:50051")
    
    # Test factorial
    result = await client.call("math.factorial", {"n": 8})
    print(f"gRPC - Factorial of 8: {result}")
    
    # Test fibonacci
    result = await client.call("math.fibonacci", {"n": 13})
    print(f"gRPC - 13th Fibonacci number: {result}")
    
    # Test square root
    result = await client.call("math.newton-sqrt", {"n": 49.0})
    print(f"gRPC - Square root of 49: {result}")

async def main():
    """Run all protocol tests."""
    print("\n=== Testing Math Service with Multiple Protocols ===\n")
    
    try:
        await test_http_client()
        print("\n---\n")
        await test_websocket_client()
        print("\n---\n")
        await test_mqtt_client()
        print("\n---\n")
        await test_grpc_client()
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    asyncio.run(main())
