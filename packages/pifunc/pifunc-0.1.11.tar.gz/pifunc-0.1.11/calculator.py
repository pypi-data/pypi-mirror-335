import os
from pifunc import service, run_services
from dotenv import load_dotenv  # If needed
# Load environment variables from .env file
load_dotenv()

# Get configuration from environment variables with defaults
API_HOST = os.getenv("API_HOST", "localhost")
API_PORT = int(os.getenv("API_PORT", 8081))


@service(http={"path": "/api/add"})
def add(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


@service(http={"path": "/api/subtract"})
def subtract(a: int, b: int) -> int:
    """Subtracts b from a."""
    return a - b


if __name__ == "__main__":
    print(f"Starting API service on {API_HOST}:{API_PORT}")
    run_services(
        http={"host": API_HOST, "port": API_PORT},
        watch=True  # Auto-reload on file changes
    )