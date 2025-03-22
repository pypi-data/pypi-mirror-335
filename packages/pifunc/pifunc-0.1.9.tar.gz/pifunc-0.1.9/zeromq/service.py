#!/usr/bin/env python3
"""
Minimal ZeroMQ service example that avoids circular imports.
"""
import os
import json
import threading
import time
import zmq

# Load environment variables from .env
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    print("dotenv not installed, using default environment variables")

# Configuration
ZMQ_HOST = os.getenv("ZMQ_HOST", "localhost")
ZMQ_ADD_PORT = int(os.getenv("ZMQ_ADD_PORT", "5555"))
ZMQ_SUBTRACT_PORT = int(os.getenv("ZMQ_SUBTRACT_PORT", "5556"))


# Service functions
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


def subtract(a: int, b: int) -> int:
    """Subtracts b from a."""
    return a - b


# ZeroMQ server implementation
def start_req_rep_server(function, port):
    """Start a REQ/REP pattern ZeroMQ server for a function."""
    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind(f"tcp://*:{port}")

    print(f"ZeroMQ REQ/REP server for {function.__name__} running on port {port}")

    running = True
    while running:
        try:
            # Wait for next request from client
            message = socket.recv()
            print(f"Received request on {function.__name__}: {message.decode('utf-8')}")

            try:
                # Parse JSON
                kwargs = json.loads(message.decode('utf-8'))

                # Call the function
                result = function(**kwargs)

                # Send reply back to client
                response = json.dumps({
                    "result": result,
                    "service": function.__name__,
                    "timestamp": time.time()
                })
                socket.send(response.encode('utf-8'))

            except json.JSONDecodeError:
                # Handle JSON parsing error
                error_response = json.dumps({
                    "error": "Invalid JSON format",
                    "service": function.__name__,
                    "timestamp": time.time()
                })
                socket.send(error_response.encode('utf-8'))

            except Exception as e:
                # Handle any other error
                error_response = json.dumps({
                    "error": str(e),
                    "service": function.__name__,
                    "timestamp": time.time()
                })
                socket.send(error_response.encode('utf-8'))
                print(f"Error processing request: {e}")

        except zmq.ZMQError as e:
            print(f"ZeroMQ error: {e}")
            time.sleep(1.0)

        except KeyboardInterrupt:
            print(f"Stopping {function.__name__} server...")
            running = False

        except Exception as e:
            print(f"Unexpected error: {e}")
            time.sleep(1.0)

    # Clean up
    socket.close()
    context.term()


def main():
    """Start all services."""
    print(f"Starting ZeroMQ services on {ZMQ_HOST}")

    # Start servers in separate threads
    threads = []

    # Add service
    add_thread = threading.Thread(
        target=start_req_rep_server,
        args=(add, ZMQ_ADD_PORT)
    )
    add_thread.daemon = True
    threads.append(add_thread)

    # Subtract service
    subtract_thread = threading.Thread(
        target=start_req_rep_server,
        args=(subtract, ZMQ_SUBTRACT_PORT)
    )
    subtract_thread.daemon = True
    threads.append(subtract_thread)

    # Start all threads
    for thread in threads:
        thread.start()

    print(f"All services started. Press Ctrl+C to exit.")

    # Keep the main thread running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down services...")


if __name__ == "__main__":
    main()