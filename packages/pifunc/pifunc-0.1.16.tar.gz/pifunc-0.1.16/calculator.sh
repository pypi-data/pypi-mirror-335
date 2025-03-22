#!/bin/bash

# Load environment variables from .env file
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
else
    echo "Error: .env file not found"
    exit 1
fi

# Define base URL using environment variables
API_HOST=${API_HOST:-localhost}
API_PORT=${API_PORT:-8081}
BASE_URL="http://${API_HOST}:${API_PORT}"

# Set text colors for better output readability
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Testing API services running on ${BASE_URL}"
echo "----------------------------------------"

# Test add endpoint
test_add() {
    local a=$1
    local b=$2
    local expected=$3

    echo -n "Testing add service with a=${a}, b=${b}: "

    response=$(curl -s -X POST "${BASE_URL}/api/add" \
        -H "Content-Type: application/json" \
        -d "{\"a\": ${a}, \"b\": ${b}}")

    # Extract the result value from the JSON response
    result=$(echo $response | grep -o '"result":[^,}]*' | cut -d':' -f2)

    if [[ "$result" == "$expected" ]]; then
        echo -e "${GREEN}PASSED${NC} (Result: ${response})"
    else
        echo -e "${RED}FAILED${NC} (Expected: ${expected}, Got: ${response})"
    fi
}

# Test subtract endpoint
test_subtract() {
    local a=$1
    local b=$2
    local expected=$3

    echo -n "Testing subtract service with a=${a}, b=${b}: "

    response=$(curl -s -X POST "${BASE_URL}/api/subtract" \
        -H "Content-Type: application/json" \
        -d "{\"a\": ${a}, \"b\": ${b}}")

    # Extract the result value from the JSON response
    result=$(echo $response | grep -o '"result":[^,}]*' | cut -d':' -f2)

    if [[ "$result" == "$expected" ]]; then
        echo -e "${GREEN}PASSED${NC} (Result: ${response})"
    else
        echo -e "${RED}FAILED${NC} (Expected: ${expected}, Got: ${response})"
    fi
}

# Run tests
echo "Testing addition service:"
test_add 5 3 8
test_add 10 20 30
test_add -5 7 2
test_add 0 0 0

echo -e "\nTesting subtraction service:"
test_subtract 10 5 5
test_subtract 5 10 -5
test_subtract 0 0 0
test_subtract -5 -3 -2

echo -e "\nAll tests completed."

# Check if service is running (optional)
echo -e "\nVerifying service health:"
if curl -s "${BASE_URL}" &> /dev/null; then
    echo -e "${GREEN}Service is running${NC}"
else
    echo -e "${RED}Service appears to be down${NC}"
    echo "Make sure your service is running with:"
    echo "python your_script.py"
fi