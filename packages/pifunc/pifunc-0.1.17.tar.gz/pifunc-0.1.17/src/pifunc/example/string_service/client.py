"""
Example client demonstrating how to use the string service through different protocols.
"""
import asyncio
import json
from pifunc import HttpClient, WebSocketClient, MqttClient, GrpcClient

async def test_http_client():
    """Test HTTP protocol endpoints."""
    client = HttpClient("http://string:8002")
    
    # Test reverse string
    text = "Hello, World!"
    result = await client.call("/api/string/reverse", {"text": text})
    print(f"HTTP - Reverse of '{text}': {result}")
    
    # Test word count
    text = "This is a test sentence"
    result = await client.call("/api/string/count-words", {"text": text})
    print(f"HTTP - Word count in '{text}': {result}")
    
    # Test title case
    text = "welcome to string service"
    result = await client.call("/api/string/to-title-case", {"text": text})
    print(f"HTTP - Title case of '{text}': {result}")

async def test_websocket_client():
    """Test WebSocket protocol endpoints."""
    client = WebSocketClient("ws://string:8082")
    await client.connect()
    
    # Test palindrome check
    text = "A man a plan a canal Panama"
    result = await client.call("string.is-palindrome", {"text": text})
    print(f"WebSocket - Is '{text}' a palindrome?: {result}")
    
    # Test find substrings
    text = "banana"
    substring = "ana"
    result = await client.call("string.find-all-substrings", {"text": text, "substring": substring})
    print(f"WebSocket - Positions of '{substring}' in '{text}': {result}")
    
    await client.disconnect()

async def test_mqtt_client():
    """Test MQTT protocol endpoints."""
    client = MqttClient("mqtt://mqtt-broker:1883")
    await client.connect()
    
    # Test reverse string
    text = "MQTT Testing"
    result = await client.call("string/reverse", {"text": text})
    print(f"MQTT - Reverse of '{text}': {result}")
    
    # Test word count
    text = "Testing with MQTT protocol"
    result = await client.call("string/count-words", {"text": text})
    print(f"MQTT - Word count in '{text}': {result}")
    
    await client.disconnect()

async def test_grpc_client():
    """Test gRPC protocol endpoints."""
    client = GrpcClient("grpc://string:50052")
    
    # Test title case
    text = "grpc string operations test"
    result = await client.call("string.to-title-case", {"text": text})
    print(f"gRPC - Title case of '{text}': {result}")
    
    # Test palindrome check
    text = "Never odd or even"
    result = await client.call("string.is-palindrome", {"text": text})
    print(f"gRPC - Is '{text}' a palindrome?: {result}")

async def main():
    """Run all protocol tests."""
    print("\n=== Testing String Service with Multiple Protocols ===\n")
    
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
