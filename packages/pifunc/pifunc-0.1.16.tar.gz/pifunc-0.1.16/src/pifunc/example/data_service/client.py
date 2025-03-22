"""
Example client demonstrating how to use the data structures service through different protocols.
"""
import asyncio
import json
from pifunc import HttpClient, WebSocketClient, MqttClient, GrpcClient

async def test_http_client():
    """Test HTTP protocol endpoints."""
    client = HttpClient("http://data:8003")
    
    # Test list sorting
    items = [5, 2, 8, 1, 9, 3]
    result = await client.call("/api/list/sort", {"items": items, "reverse": True})
    print(f"HTTP - Sort list {items} in reverse: {result}")
    
    # Test remove duplicates
    items = [1, 2, 2, 3, 3, 4, 1, 5]
    result = await client.call("/api/list/remove-duplicates", {"items": items})
    print(f"HTTP - Remove duplicates from {items}: {result}")

async def test_websocket_client():
    """Test WebSocket protocol endpoints."""
    client = WebSocketClient("ws://data:8083")
    await client.connect()
    
    # Test merge dictionaries
    dict1 = {"a": 1, "b": 2}
    dict2 = {"b": 3, "c": 4}
    result = await client.call("dict.merge", {"dict1": dict1, "dict2": dict2})
    print(f"WebSocket - Merge dictionaries {dict1} and {dict2}: {result}")
    
    # Test find in list
    items = ["apple", "banana", "orange", "grape"]
    target = "orange"
    result = await client.call("list.find", {"items": items, "target": target})
    print(f"WebSocket - Find '{target}' in {items}: at index {result}")
    
    await client.disconnect()

async def test_mqtt_client():
    """Test MQTT protocol endpoints."""
    client = MqttClient("mqtt://mqtt-broker:1883")
    await client.connect()
    
    # Test list sorting
    items = ["zebra", "ant", "bear", "cat"]
    result = await client.call("list/sort", {"items": items})
    print(f"MQTT - Sort list {items}: {result}")
    
    # Test filter dictionary
    data = {"a": 10, "b": 20, "c": 5, "d": 15}
    result = await client.call("dict/filter-by-value", {"data": data, "predicate": ">10"})
    print(f"MQTT - Filter dictionary {data} where value > 10: {result}")
    
    await client.disconnect()

async def test_grpc_client():
    """Test gRPC protocol endpoints."""
    client = GrpcClient("grpc://data:50053")
    
    # Test remove duplicates with mixed types
    items = [1, "hello", 2, "hello", 3, 1, "world"]
    result = await client.call("list.remove-duplicates", {"items": items})
    print(f"gRPC - Remove duplicates from {items}: {result}")
    
    # Test merge dictionaries with nested data
    dict1 = {"settings": {"theme": "dark"}, "version": 1}
    dict2 = {"settings": {"language": "en"}, "version": 2}
    result = await client.call("dict.merge", {"dict1": dict1, "dict2": dict2})
    print(f"gRPC - Merge complex dictionaries: {result}")

async def main():
    """Run all protocol tests."""
    print("\n=== Testing Data Structures Service with Multiple Protocols ===\n")
    
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
