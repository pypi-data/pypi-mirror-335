"""
Example client demonstrating how to interact with calculator service using different protocols.
"""
import asyncio
from pifunc import http_client, websocket_client, redis_client, mqtt_client

async def demo_http():
    """Demonstrate HTTP client usage."""
    print("\n=== HTTP Client Demo ===")
    # Using HTTP client
    result = await http_client.get("http://calculator:8000/api/calculator/add", params={"a": 5, "b": 3})
    print(f"HTTP Add (5 + 3) = {result['result']}")
    
    result = await http_client.get("http://calculator:8000/api/calculator/multiply", params={"a": 4, "b": 6})
    print(f"HTTP Multiply (4 * 6) = {result}")

async def demo_websocket():
    """Demonstrate WebSocket client usage."""
    print("\n=== WebSocket Client Demo ===")
    # Using WebSocket client
    async with websocket_client.connect("ws://calculator:8080") as ws:
        result = await ws.call("calculator.add", 10, 5)
        print(f"WebSocket Add (10 + 5) = {result}")
        
        result = await ws.call("calculator.multiply", 3, 7)
        print(f"WebSocket Multiply (3 * 7) = {result}")

async def demo_redis():
    """Demonstrate Redis client usage."""
    print("\n=== Redis Client Demo ===")
    # Using Redis client for pub/sub
    async with redis_client.connect("redis://redis:6379") as redis:
        await redis.publish("calc_channel", {"operation": "add", "a": 15, "b": 5})
        result = await redis.subscribe("calc_result")
        print(f"Redis Pub/Sub calculation result: {result}")

async def demo_mqtt():
    """Demonstrate MQTT client usage."""
    print("\n=== MQTT Client Demo ===")
    # Using MQTT client
    async with mqtt_client.connect("mqtt://mqtt-broker:1883") as mqtt:
        await mqtt.publish("calculator/add", {"a": 20, "b": 10})
        result = await mqtt.subscribe("calculator/result")
        print(f"MQTT calculation result: {result}")

async def main():
    """Run all protocol demonstrations."""
    print("Starting protocol demonstrations...")
    
    try:
        await demo_http()
    except Exception as e:
        print(f"HTTP demo error: {e}")
    
    try:
        await demo_websocket()
    except Exception as e:
        print(f"WebSocket demo error: {e}")
    
    try:
        await demo_redis()
    except Exception as e:
        print(f"Redis demo error: {e}")
    
    try:
        await demo_mqtt()
    except Exception as e:
        print(f"MQTT demo error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
