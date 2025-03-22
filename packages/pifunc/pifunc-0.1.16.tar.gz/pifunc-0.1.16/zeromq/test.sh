#!/bin/bash

echo "ZeroMQ Simple Connection Test"
echo "============================"

# A simple server in one process
start_server() {
    echo "Starting ZeroMQ REP server on port 5555..."
    python3 -c "
import zmq
import time
import signal
import sys

def signal_handler(sig, frame):
    print('Server shutting down...')
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)

context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind('tcp://*:5555')
print('Server ready, waiting for requests...')

while True:
    try:
        # Wait for next request from client
        message = socket.recv()
        print(f'Received request: {message.decode()}')

        # Simulate work
        time.sleep(1)

        # Send reply
        socket.send(b'Response from server')
    except zmq.ZMQError as e:
        print(f'ZMQ Error: {e}')
        break
    except Exception as e:
        print(f'Error: {e}')
        break

socket.close()
context.term()
" &

SERVER_PID=$!
echo "Server started with PID: $SERVER_PID"

# Wait for server to start
sleep 2
}

# A simple client to test connectivity
test_client() {
    echo "Testing client connection to localhost:5555..."
    python3 -c "
import zmq
import time

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect('tcp://localhost:5555')

print('Sending request...')
socket.send(b'Hello from client')

# Use poller to add timeout
poller = zmq.Poller()
poller.register(socket, zmq.POLLIN)

# Wait up to 5 seconds for response
if poller.poll(5000):
    response = socket.recv()
    print(f'Received response: {response.decode()}')
    print('Connection successful!')
else:
    print('Error: Timeout - no response received')
    print('Connection failed.')

socket.close()
context.term()
"
    CLIENT_RESULT=$?
    return $CLIENT_RESULT
}

# Cleanup function to kill the server
cleanup() {
    if [ -n "$SERVER_PID" ]; then
        echo "Stopping server (PID: $SERVER_PID)..."
        kill $SERVER_PID >/dev/null 2>&1
        wait $SERVER_PID >/dev/null 2>&1
    fi
    echo "Test completed."
}

# Set trap to ensure cleanup on exit
trap cleanup EXIT INT

# Run the test
start_server
test_client

if [ $? -eq 0 ]; then
    echo -e "\033[0;32mBasic ZeroMQ connectivity test PASSED\033[0m"
    echo "If your main service tests are failing, check for:"
    echo "1. Correct ports in .env file"
    echo "2. Service implementation issues"
    echo "3. Firewall or network restrictions"
else
    echo -e "\033[0;31mBasic ZeroMQ connectivity test FAILED\033[0m"
    echo "Possible issues:"
    echo "1. ZeroMQ installation problem"
    echo "2. Port 5555 is blocked or in use"
    echo "3. Firewall or network restrictions"
    echo "4. Python environment issues"
fi