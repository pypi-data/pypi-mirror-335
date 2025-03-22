"""
String service demonstrating various string operations through multiple protocols.
"""
from pifunc import http, mqtt, websocket, grpc
from typing import List

@http("/api/string/reverse")
@mqtt("string/reverse")
@websocket("string.reverse")
@grpc("string.reverse")
def reverse_string(text: str) -> str:
    """Reverse a string."""
    return text[::-1]

@http("/api/string/count-words")
@mqtt("string/count-words")
@websocket("string.count-words")
@grpc("string.count-words")
def count_words(text: str) -> int:
    """Count the number of words in a string."""
    if not text.strip():
        return 0
    return len(text.split())

@http("/api/string/to-title-case")
@mqtt("string/to-title-case")
@websocket("string.to-title-case")
@grpc("string.to-title-case")
def to_title_case(text: str) -> str:
    """Convert string to title case."""
    return text.title()

@http("/api/string/is-palindrome")
@mqtt("string/is-palindrome")
@websocket("string.is-palindrome")
@grpc("string.is-palindrome")
def is_palindrome(text: str) -> bool:
    """Check if a string is a palindrome."""
    cleaned = ''.join(c.lower() for c in text if c.isalnum())
    return cleaned == cleaned[::-1]

@http("/api/string/find-all-substrings")
@mqtt("string/find-all-substrings")
@websocket("string.find-all-substrings")
@grpc("string.find-all-substrings")
def find_all_substrings(text: str, substring: str) -> List[int]:
    """Find all occurrences of a substring in text and return their positions."""
    positions = []
    pos = text.find(substring)
    while pos != -1:
        positions.append(pos)
        pos = text.find(substring, pos + 1)
    return positions

if __name__ == "__main__":
    print("String Service started. Available protocols:")
    print("- HTTP on port 8002")
    print("- WebSocket on port 8082")
    print("- MQTT on port 1883")
    print("- gRPC on port 50052")
