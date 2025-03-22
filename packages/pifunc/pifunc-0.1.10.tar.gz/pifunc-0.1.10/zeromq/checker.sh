#!/bin/bash

# Define colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
NC='\033[0m' # No Color

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo -e "${RED}Error: .env file not found${NC}"
    exit 1
fi

# Set default values if environment variables are not set
ZMQ_HOST=${ZMQ_HOST:-localhost}
ZMQ_ADD_PORT=${ZMQ_ADD_PORT:-5555}
ZMQ_SUBTRACT_PORT=${ZMQ_SUBTRACT_PORT:-5556}
ZMQ_STATUS_PORT=${ZMQ_STATUS_PORT:-5557}
ZMQ_PROCESS_TASK_PORT=${ZMQ_PROCESS_TASK_PORT:-5558}

echo -e "${YELLOW}ZeroMQ Service Availability Checker${NC}"
echo "========================================"

# Check if a port is in use (which might indicate a service is running)
check_port() {
    local host=$1
    local port=$2
    local service=$3

    # Try to connect using netcat with a short timeout
    if command -v nc >/dev/null 2>&1; then
        nc -z -w 1 $host $port >/dev/null 2>&1
        result=$?
    else
        # If netcat is not available, try telnet
        (echo > /dev/tcp/$host/$port) >/dev/null 2>&1
        result=$?
    fi

    if [ $result -eq 0 ]; then
        echo -e "${GREEN}✓ $service (${host}:${port}) appears to be running${NC}"
        return 0
    else
        echo -e "${RED}✗ $service (${host}:${port}) does not appear to be running${NC}"
        return 1
    fi
}

# Check for running Python processes related to ZeroMQ
check_python_processes() {
    echo -e "\n${YELLOW}Checking for running Python processes:${NC}"

    # Look for Python processes with 'zeromq' in the command line
    pids=$(ps aux | grep -i 'python.*zeromq' | grep -v grep | awk '{print $2}')

    if [ -z "$pids" ]; then
        echo -e "${RED}No Python processes related to ZeroMQ were found${NC}"
        echo -e "Make sure you've started the ZeroMQ service with:"
        echo -e "  ${YELLOW}python zeromq-service.py${NC}"
        return 1
    else
        echo -e "${GREEN}Found ZeroMQ-related Python processes:${NC}"
        ps aux | grep -i 'python.*zeromq' | grep -v grep
        return 0
    fi
}

# Check if ZeroMQ Python package is installed
check_zmq_installation() {
    echo -e "\n${YELLOW}Checking ZeroMQ Python package installation:${NC}"

    if python3 -c "import zmq; print(f'ZeroMQ version: {zmq.__version__}')" 2>/dev/null; then
        return 0
    else
        echo -e "${RED}ZeroMQ Python package is not installed${NC}"
        echo -e "Install it with:"
        echo -e "  ${YELLOW}pip install pyzmq${NC}"
        return 1
    fi
}

# Check if required ports are in use
check_ports() {
    echo -e "\n${YELLOW}Checking service ports:${NC}"
    local all_available=0

    check_port $ZMQ_HOST $ZMQ_ADD_PORT "Add service" || all_available=1
    check_port $ZMQ_HOST $ZMQ_SUBTRACT_PORT "Subtract service" || all_available=1
    check_port $ZMQ_HOST $ZMQ_STATUS_PORT "Status service" || all_available=1
    check_port $ZMQ_HOST $ZMQ_PROCESS_TASK_PORT "Process task service" || all_available=1

    return $all_available
}

# Main function
main() {
    check_zmq_installation
    check_python_processes
    check_ports

    local exit_code=$?

    echo -e "\n${YELLOW}Recommendations:${NC}"
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}All checks passed. Services appear to be running.${NC}"
        echo -e "You can run the test client with:"
        echo -e "  ${YELLOW}./zeromq-client.sh${NC}"
    else
        echo -e "${RED}Some checks failed. Please ensure:${NC}"
        echo -e "1. ZeroMQ Python package is installed: ${YELLOW}pip install pyzmq${NC}"
        echo -e "2. The ZeroMQ service is running: ${YELLOW}python zeromq-service.py${NC}"
        echo -e "3. The ports in .env file match the ports used by the service"
        echo -e "4. No firewalls are blocking the required ports"
        echo -e "\nCheck the service logs for more information."
    fi

    exit $exit_code
}

# Run the main function
main