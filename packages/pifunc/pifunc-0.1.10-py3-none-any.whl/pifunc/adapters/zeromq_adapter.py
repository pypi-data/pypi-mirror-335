# pifunc/adapters/zeromq_adapter.py
import json
import asyncio
import threading
import time
import inspect
import os
from typing import Any, Callable, Dict, List, Optional
# Import only ZeroMQ functionality
from pifunc.adapters import ProtocolAdapter
# Your service code here
import zmq
import zmq.asyncio


class ZeroMQAdapter(ProtocolAdapter):
    """ZeroMQ protocol adapter."""

    def __init__(self):
        self.context = None
        self.functions = {}
        self.config = {}
        self.sockets = {}
        self.running = False
        self.server_threads = []

    def setup(self, config: Dict[str, Any]) -> None:
        """Configure the ZeroMQ adapter."""
        self.config = config

        # Create ZeroMQ context
        self.context = zmq.Context()

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Register a function as a ZeroMQ endpoint."""
        service_name = metadata.get("name", func.__name__)

        # Get ZeroMQ configuration
        zmq_config = metadata.get("zeromq", {})

        # Determine the communication pattern
        pattern = zmq_config.get("pattern", "REQ_REP")

        # Use environment variables if available, otherwise use config values
        port_env_var = f"ZMQ_{service_name.upper()}_PORT"
        port = int(os.getenv(port_env_var, zmq_config.get("port", 0)))  # 0 means auto-assign port

        bind_address_env_var = f"ZMQ_{service_name.upper()}_BIND_ADDRESS"
        bind_address = os.getenv(bind_address_env_var, zmq_config.get("bind_address", "tcp://*"))

        topic_env_var = f"ZMQ_{service_name.upper()}_TOPIC"
        topic = os.getenv(topic_env_var, zmq_config.get("topic", service_name))

        # Store function information
        self.functions[service_name] = {
            "function": func,
            "metadata": metadata,
            "pattern": pattern,
            "port": port,
            "bind_address": bind_address,
            "topic": topic,
            "socket": None,
            "thread": None
        }

    def _create_socket(self, pattern: str) -> zmq.Socket:
        """Create a ZeroMQ socket of the appropriate type."""
        if pattern == "REQ_REP":
            return self.context.socket(zmq.REP)
        elif pattern == "PUB_SUB":
            return self.context.socket(zmq.PUB)
        elif pattern == "PUSH_PULL":
            return self.context.socket(zmq.PULL)
        elif pattern == "ROUTER_DEALER":
            return self.context.socket(zmq.ROUTER)
        else:
            raise ValueError(f"Unsupported ZeroMQ pattern: {pattern}")

    def _req_rep_server(self, service_name: str, function_info: Dict[str, Any]):
        """Server for the REQ/REP pattern."""
        socket = self._create_socket("REQ_REP")

        # Bind the socket
        if function_info["port"] > 0:
            bind_address = f"{function_info['bind_address']}:{function_info['port']}"
            socket.bind(bind_address)
            actual_port = function_info["port"]
        else:
            # Auto-assign port
            bind_address = f"{function_info['bind_address']}:*"
            actual_port = socket.bind_to_random_port(bind_address)

        print(f"ZeroMQ REQ/REP server for {service_name} running on port {actual_port}")

        # Update port information
        function_info["port"] = actual_port
        function_info["socket"] = socket

        # Main loop
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        func = function_info["function"]

        while self.running:
            try:
                # Wait for message with timeout
                socks = dict(poller.poll(1000))  # 1s timeout

                if socket in socks and socks[socket] == zmq.POLLIN:
                    # Receive message
                    message = socket.recv()

                    try:
                        # Parse JSON
                        kwargs = json.loads(message.decode('utf-8'))

                        # Call the function
                        result = func(**kwargs)

                        # Handle coroutines
                        if asyncio.iscoroutine(result):
                            # Create a new asyncio loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(result)
                            loop.close()

                        # Serialize the result
                        response = json.dumps({
                            "result": result,
                            "service": service_name,
                            "timestamp": time.time()
                        })

                        # Send response
                        socket.send(response.encode('utf-8'))

                    except json.JSONDecodeError:
                        # Send error information
                        error_response = json.dumps({
                            "error": "Invalid JSON format",
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        socket.send(error_response.encode('utf-8'))
                    except Exception as e:
                        # Send error information
                        error_response = json.dumps({
                            "error": str(e),
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        socket.send(error_response.encode('utf-8'))
                        print(f"Error processing message: {e}")

            except zmq.ZMQError as e:
                print(f"ZeroMQ error: {e}")
                time.sleep(1.0)
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1.0)

        # Close socket
        socket.close()

    def _router_dealer_server(self, service_name: str, function_info: Dict[str, Any]):
        """Server for the ROUTER/DEALER pattern."""
        socket = self._create_socket("ROUTER_DEALER")

        # Bind the socket
        if function_info["port"] > 0:
            bind_address = f"{function_info['bind_address']}:{function_info['port']}"
            socket.bind(bind_address)
            actual_port = function_info["port"]
        else:
            # Auto-assign port
            bind_address = f"{function_info['bind_address']}:*"
            actual_port = socket.bind_to_random_port(bind_address)

        print(f"ZeroMQ ROUTER server for {service_name} running on port {actual_port}")

        # Update port information
        function_info["port"] = actual_port
        function_info["socket"] = socket

        # Main loop
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        func = function_info["function"]

        while self.running:
            try:
                # Wait for message with timeout
                socks = dict(poller.poll(1000))  # 1s timeout

                if socket in socks and socks[socket] == zmq.POLLIN:
                    # Receive message (client ID + empty frame + data)
                    client_id, empty, message = socket.recv_multipart()

                    try:
                        # Parse JSON
                        kwargs = json.loads(message.decode('utf-8'))

                        # Call the function
                        result = func(**kwargs)

                        # Handle coroutines
                        if asyncio.iscoroutine(result):
                            # Create a new asyncio loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(result)
                            loop.close()

                        # Serialize the result
                        response = json.dumps({
                            "result": result,
                            "service": service_name,
                            "timestamp": time.time()
                        })

                        # Send response maintaining the multipart format
                        socket.send_multipart([client_id, empty, response.encode('utf-8')])

                    except json.JSONDecodeError:
                        # Send error information
                        error_response = json.dumps({
                            "error": "Invalid JSON format",
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        socket.send_multipart([client_id, empty, error_response.encode('utf-8')])
                    except Exception as e:
                        # Send error information
                        error_response = json.dumps({
                            "error": str(e),
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        socket.send_multipart([client_id, empty, error_response.encode('utf-8')])
                        print(f"Error processing message: {e}")

            except zmq.ZMQError as e:
                print(f"ZeroMQ error: {e}")
                time.sleep(1.0)
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1.0)

        # Close socket
        socket.close()

    def _pub_sub_server(self, service_name: str, function_info: Dict[str, Any]):
        """Server for the PUB/SUB pattern."""
        socket = self._create_socket("PUB_SUB")

        # Bind the socket
        if function_info["port"] > 0:
            bind_address = f"{function_info['bind_address']}:{function_info['port']}"
            socket.bind(bind_address)
            actual_port = function_info["port"]
        else:
            # Auto-assign port
            bind_address = f"{function_info['bind_address']}:*"
            actual_port = socket.bind_to_random_port(bind_address)

        print(f"ZeroMQ PUB server for {service_name} running on port {actual_port}")

        # Update port information
        function_info["port"] = actual_port
        function_info["socket"] = socket

        # For PUB/SUB, we use a separate thread to periodically call the function
        # and publish the results

        topic = function_info["topic"]
        func = function_info["function"]
        interval = function_info.get("metadata", {}).get("zeromq", {}).get("interval", 1.0)

        while self.running:
            try:
                # Call the function
                result = func()

                # Handle coroutines
                if asyncio.iscoroutine(result):
                    # Create a new asyncio loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(result)
                    loop.close()

                # Serialize the result
                message = json.dumps({
                    "result": result,
                    "service": service_name,
                    "timestamp": time.time()
                })

                # Publish the message with the topic
                socket.send_multipart([
                    topic.encode('utf-8'),
                    message.encode('utf-8')
                ])

                # Wait for the next iteration
                time.sleep(interval)

            except Exception as e:
                print(f"Error in PUB/SUB server for {service_name}: {e}")
                time.sleep(1.0)

        # Close socket
        socket.close()

    def _push_pull_server(self, service_name: str, function_info: Dict[str, Any]):
        """Server for the PUSH/PULL pattern."""
        socket = self._create_socket("PUSH_PULL")

        # Bind the socket
        if function_info["port"] > 0:
            bind_address = f"{function_info['bind_address']}:{function_info['port']}"
            socket.bind(bind_address)
            actual_port = function_info["port"]
        else:
            # Auto-assign port
            bind_address = f"{function_info['bind_address']}:*"
            actual_port = socket.bind_to_random_port(bind_address)

        print(f"ZeroMQ PULL server for {service_name} running on port {actual_port}")

        # Update port information
        function_info["port"] = actual_port
        function_info["socket"] = socket

        # Main loop
        poller = zmq.Poller()
        poller.register(socket, zmq.POLLIN)

        func = function_info["function"]

        # Create response socket
        push_socket = self.context.socket(zmq.PUSH)

        # Get response port from environment variable or config
        response_port_env_var = f"ZMQ_{service_name.upper()}_RESPONSE_PORT"
        response_port = int(os.getenv(response_port_env_var,
                                      self.config.get("response_port", actual_port + 1)))

        push_socket.bind(f"{function_info['bind_address']}:{response_port}")
        print(f"ZeroMQ PUSH response server for {service_name} running on port {response_port}")

        while self.running:
            try:
                # Wait for message with timeout
                socks = dict(poller.poll(1000))  # 1s timeout

                if socket in socks and socks[socket] == zmq.POLLIN:
                    # Receive message
                    message = socket.recv()

                    try:
                        # Parse JSON
                        message_data = json.loads(message.decode('utf-8'))
                        kwargs = message_data.get("data", {})
                        response_id = message_data.get("response_id", None)

                        # Call the function
                        result = func(**kwargs)

                        # Handle coroutines
                        if asyncio.iscoroutine(result):
                            # Create a new asyncio loop
                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)
                            result = loop.run_until_complete(result)
                            loop.close()

                        # Serialize the result
                        response = json.dumps({
                            "result": result,
                            "service": service_name,
                            "timestamp": time.time(),
                            "response_id": response_id
                        })

                        # Send response
                        push_socket.send(response.encode('utf-8'))

                    except json.JSONDecodeError:
                        # Send error information
                        error_response = json.dumps({
                            "error": "Invalid JSON format",
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        push_socket.send(error_response.encode('utf-8'))
                    except Exception as e:
                        # Send error information
                        error_response = json.dumps({
                            "error": str(e),
                            "service": service_name,
                            "timestamp": time.time()
                        })
                        push_socket.send(error_response.encode('utf-8'))
                        print(f"Error processing message: {e}")

            except zmq.ZMQError as e:
                print(f"ZeroMQ error: {e}")
                time.sleep(1.0)
            except Exception as e:
                print(f"Unexpected error: {e}")
                time.sleep(1.0)

        # Close sockets
        socket.close()
        push_socket.close()

    def start(self) -> None:
        """Start the ZeroMQ adapter."""
        if self.running:
            return

        self.running = True

        # Start servers for all registered functions
        for service_name, function_info in self.functions.items():
            pattern = function_info["pattern"]

            # Choose the appropriate server type
            if pattern == "REQ_REP":
                thread = threading.Thread(
                    target=self._req_rep_server,
                    args=(service_name, function_info)
                )
            elif pattern == "PUB_SUB":
                thread = threading.Thread(
                    target=self._pub_sub_server,
                    args=(service_name, function_info)
                )
            elif pattern == "PUSH_PULL":
                thread = threading.Thread(
                    target=self._push_pull_server,
                    args=(service_name, function_info)
                )
            elif pattern == "ROUTER_DEALER":
                thread = threading.Thread(
                    target=self._router_dealer_server,
                    args=(service_name, function_info)
                )
            else:
                print(f"Unsupported ZeroMQ pattern: {pattern}")
                continue

            # Start the server thread
            thread.daemon = True
            thread.start()

            # Store the thread
            function_info["thread"] = thread
            self.server_threads.append(thread)

        print(f"ZeroMQ adapter started with {len(self.server_threads)} servers")

    def stop(self) -> None:
        """Stop the ZeroMQ adapter."""
        if not self.running:
            return

        self.running = False

        # Wait for threads to finish
        for thread in self.server_threads:
            thread.join(timeout=2.0)

        # Close all sockets
        for service_name, function_info in self.functions.items():
            socket = function_info.get("socket")
            if socket:
                try:
                    socket.close()
                except:
                    pass

        # Close the ZeroMQ context
        try:
            self.context.term()
        except:
            pass

        self.server_threads = []
        print("ZeroMQ adapter stopped")