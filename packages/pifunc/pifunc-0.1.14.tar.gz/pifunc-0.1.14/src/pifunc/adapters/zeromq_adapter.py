# pifunc/adapters/zeromq_adapter.py
import json
import asyncio
import threading
import time
import inspect
import os
from typing import Any, Callable, Dict, List, Optional
from pifunc.adapters import ProtocolAdapter
import logging

logger = logging.getLogger(__name__)

# Try to import ZeroMQ, but handle missing dependency gracefully
try:
    import zmq
    import zmq.asyncio
    _zeromq_available = True
except ImportError:
    _zeromq_available = False
    print("Warning: ZeroMQ library not available. ZeroMQ adapter will be disabled.")


class ZeroMQAdapter(ProtocolAdapter):
    """ZeroMQ protocol adapter."""

    def __init__(self):
        self.context = None
        self.functions = {}
        self.config = {}
        self.sockets = {}
        self.running = False
        self.server_threads = []
        self._connected = _zeromq_available

    def setup(self, config: Dict[str, Any]) -> None:
        """Configure the ZeroMQ adapter."""
        self.config = config
        # Add force connection flag
        self.force_connection = config.get("force_connection", False)

        if not _zeromq_available:
            if self.force_connection:
                raise ImportError("ZeroMQ library is required but not available.")
            self._connected = False
            return

        try:
            # Create ZeroMQ context
            self.context = zmq.Context()
            self._connected = True
        except Exception as e:
            logger.warning(f"Failed to initialize ZeroMQ context: {e}")
            print(f"Warning: Failed to initialize ZeroMQ context: {e}")
            print("ZeroMQ features will be disabled. Set force_connection=True to require ZeroMQ.")
            self._connected = False

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Register a function as a ZeroMQ endpoint."""
        if not self._connected:
            logger.warning(f"Not connected to ZeroMQ, skipping registration of {func.__name__}")
            print(f"Not connected to ZeroMQ, skipping registration of {func.__name__}")
            return

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

    def _create_socket(self, pattern: str) -> Any:
        """Create a ZeroMQ socket of the appropriate type."""
        if not self._connected:
            return None

        try:
            if pattern == "REQ_REP":
                return self.context.socket(zmq.REP)
            elif pattern == "PUB_SUB":
                return self.context.socket(zmq.PUB)
            elif pattern == "PUSH_PULL":
                return self.context.socket(zmq.PULL)
            elif pattern == "ROUTER_DEALER":
                return self.context.socket(zmq.ROUTER)
            else:
                logger.error(f"Unsupported ZeroMQ pattern: {pattern}")
                return None
        except Exception as e:
            logger.error(f"Error creating ZeroMQ socket: {e}")
            return None

    def _req_rep_server(self, service_name: str, function_info: Dict[str, Any]):
        """Server for the REQ/REP pattern."""
        if not self._connected:
            return

        socket = self._create_socket("REQ_REP")
        if not socket:
            logger.error(f"Could not create REQ/REP socket for {service_name}")
            return

        # Bind the socket
        try:
            if function_info["port"] > 0:
                bind_address = f"{function_info['bind_address']}:{function_info['port']}"
                socket.bind(bind_address)
                actual_port = function_info["port"]
            else:
                # Auto-assign port - safer implementation
                bind_address = function_info['bind_address']
                if not bind_address.endswith(':'):
                    bind_address += ':'
                actual_port = socket.bind_to_random_port(bind_address)

            logger.info(f"ZeroMQ REQ/REP server for {service_name} running on port {actual_port}")
            print(f"ZeroMQ REQ/REP server for {service_name} running on port {actual_port}")

            # Update port information
            function_info["port"] = actual_port
            function_info["socket"] = socket
        except zmq.ZMQError as e:
            logger.error(f"Error binding ZeroMQ socket for {service_name}: {e}")
            print(f"Error binding ZeroMQ socket for {service_name}: {e}")
            socket.close()
            return

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
                        logger.error(f"Error processing message: {e}")

            except zmq.ZMQError as e:
                logger.error(f"ZeroMQ error: {e}")
                time.sleep(1.0)
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                time.sleep(1.0)

        # Close socket
        socket.close()

    def start(self) -> None:
        """Start the ZeroMQ adapter."""
        if self.running or not self._connected:
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
                logger.warning(f"PUB/SUB pattern not fully implemented for {service_name}")
                continue
            elif pattern == "PUSH_PULL":
                logger.warning(f"PUSH/PULL pattern not fully implemented for {service_name}")
                continue
            elif pattern == "ROUTER_DEALER":
                logger.warning(f"ROUTER/DEALER pattern not fully implemented for {service_name}")
                continue
            else:
                logger.error(f"Unsupported ZeroMQ pattern: {pattern}")
                continue

            # Start the server thread
            thread.daemon = True
            thread.start()

            # Store the thread
            function_info["thread"] = thread
            self.server_threads.append(thread)

        logger.info(f"ZeroMQ adapter started with {len(self.server_threads)} servers")
        print(f"ZeroMQ adapter started with {len(self.server_threads)} servers")

    def stop(self) -> None:
        """Stop the ZeroMQ adapter."""
        if not self.running or not self._connected:
            return

        self.running = False

        # Wait for threads to finish
        for thread in self.server_threads:
            try:
                thread.join(timeout=2.0)
            except Exception as e:
                logger.error(f"Error stopping ZeroMQ thread: {e}")

        # Close all sockets
        for service_name, function_info in self.functions.items():
            socket = function_info.get("socket")
            if socket:
                try:
                    socket.close()
                except Exception as e:
                    logger.error(f"Error closing ZeroMQ socket: {e}")

        # Close the ZeroMQ context
        try:
            self.context.term()
        except Exception as e:
            logger.error(f"Error terminating ZeroMQ context: {e}")

        self.server_threads = []
        logger.info("ZeroMQ adapter stopped")
        print("ZeroMQ adapter stopped")