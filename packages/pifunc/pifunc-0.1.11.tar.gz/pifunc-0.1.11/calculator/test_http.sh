#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Base URL for the calculator service
BASE_URL="http://localhost:8090"

# Function to test an endpoint
test_endpoint() {
    local endpoint=$1
    local data=$2
    local expected=$3
    local description=$4

    echo -e "\nTesting $description..."
    
    response=$(curl -s -X POST \
        -H "Content-Type: application/json" \
        -d "$data" \
        "${BASE_URL}${endpoint}")
    COMM="curl -s -X POST -H \"Content-Type: application/json\" -d '$data' \"${BASE_URL}${endpoint}\""
    echo $COMM

    if [[ "$response" == *"$expected"* ]]; then
        echo -e "${GREEN}✓ Test passed${NC}"
        echo "Expected: $expected"
        echo "Got: $response"
    else
        echo -e "${RED}✗ Test failed${NC}"
        echo "Expected: $expected"
        echo "Got: $response"
    fi
}

# Test calculator HTML interface
echo "Testing calculator HTML interface..."
response=$(curl -s "${BASE_URL}/calculator")
if [[ "$response" == *"html"* ]]; then
    echo -e "${GREEN}✓ HTML interface test passed${NC}"
else
    echo -e "${RED}✗ HTML interface test failed${NC}"
fi

# Test addition
test_endpoint "/api/calculator/add" '{"a": 5, "b": 3}' '"result":8' "addition (5 + 3)"
test_endpoint "/api/calculator/add" '{"a": -2, "b": 3}' '"result":1' "addition with negative number (-2 + 3)"

# Test multiplication
test_endpoint "/api/calculator/multiply" '{"a": 4, "b": 3}' '12' "multiplication (4 * 3)"
test_endpoint "/api/calculator/multiply" '{"a": -2, "b": 3}' '-6' "multiplication with negative number (-2 * 3)"
test_endpoint "/api/calculator/multiply" '{"a": 5, "b": 0}' '0' "multiplication by zero (5 * 0)"

# Test division
test_endpoint "/api/calculator/divide" '{"a": 6, "b": 2}' '3' "division (6 / 2)"
test_endpoint "/api/calculator/divide" '{"a": -6, "b": 2}' '-3' "division with negative number (-6 / 2)"
test_endpoint "/api/calculator/divide" '{"a": 5, "b": 0}' 'Division by zero' "division by zero error (5 / 0)"

# Test subtraction
test_endpoint "/api/calculator/subtract" '{"a": 5, "b": 3}' '2' "subtraction (5 - 3)"
test_endpoint "/api/calculator/subtract" '{"a": -2, "b": 3}' '-5' "subtraction with negative number (-2 - 3)"
test_endpoint "/api/calculator/subtract" '{"a": 5, "b": 0}' '5' "subtraction with zero (5 - 0)"

echo -e "\nAll tests completed!"
