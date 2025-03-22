# pifunc_client.py
import json
import requests


class PiFuncClient:
    """Simple client for pifunc services."""

    def __init__(self, base_url="http://localhost:8080", protocol="http"):
        """
        Initialize the pifunc client.

        Args:
            base_url: Base URL for the HTTP protocol
            protocol: Default protocol to use ('http', 'grpc', etc.)
        """
        self.base_url = base_url
        self.protocol = protocol.lower()
        self._session = requests.Session()

    def call(self, service_name, args=None, **kwargs):
        """
        Call a remote service.

        Args:
            service_name: Name of the service to call
            args: Arguments to pass to the service
            **kwargs: Additional protocol-specific configuration

        Returns:
            Result of the service call
        """
        if args is None:
            args = {}

        # Determine which protocol to use
        protocol = kwargs.get('protocol', self.protocol)

        # Call service based on protocol
        if protocol == "http":
            path = kwargs.get("path", f"/api/{service_name}")
            method = kwargs.get("method", "POST")

            url = f"{self.base_url}{path}"

            if method.upper() == "GET":
                response = self._session.get(url, params=args)
            else:
                response = self._session.post(url, json=args)

            try:
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                print(f"HTTP request error: {e}")
                return {"error": str(e)}
            except ValueError:
                return {"result": response.text}
        else:
            print(f"Protocol {protocol} is not implemented yet")
            return {"error": f"Protocol {protocol} not implemented"}

    def close(self):
        """Close all connections."""
        self._session.close()