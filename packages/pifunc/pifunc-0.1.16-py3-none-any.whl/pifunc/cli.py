#!/usr/bin/env python3
"""
PIfunc Command Line Interface

This module provides a command-line interface for interacting with PIfunc services,
calling functions, generating client code, and viewing documentation.
"""

import argparse
import json
import os
import sys
import requests
import importlib
import inspect
import pkg_resources
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("pifunc.cli")


def setup_logging(level=logging.INFO):
    """Configure logging for the CLI."""
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="PIfunc Command Line Interface")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    # Call command
    call_parser = subparsers.add_parser("call", help="Call a PIfunc function")
    call_parser.add_argument("function", help="Function name to call")
    call_parser.add_argument("--args", help="Arguments as JSON string", default="{}")
    call_parser.add_argument("--protocol", help="Protocol to use (default: http)", default="http")
    call_parser.add_argument("--host", help="Host to connect to", default="localhost")
    call_parser.add_argument("--port", help="Port to connect to", type=int)
    call_parser.add_argument("--path", help="Path for HTTP requests (default: /api/{function})")
    call_parser.add_argument("--method", help="HTTP method (default: POST)", default="POST")
    call_parser.add_argument("--timeout", help="Request timeout in seconds", type=int, default=30)

    # Generate command
    gen_parser = subparsers.add_parser("generate", help="Generate client code")
    gen_parser.add_argument("type", choices=["client"], help="Type of code to generate")
    gen_parser.add_argument("--language", choices=["python", "javascript", "typescript"],
                            help="Programming language", default="python")
    gen_parser.add_argument("--output", help="Output file path")
    gen_parser.add_argument("--host", help="Host for client connection", default="localhost")
    gen_parser.add_argument("--port", help="Port for client connection", type=int)
    gen_parser.add_argument("--protocol", help="Protocol for client (default: http)", default="http")
    gen_parser.add_argument("--module", help="Python module with service definitions")

    # Docs command
    docs_parser = subparsers.add_parser("docs", help="View service documentation")
    docs_parser.add_argument("action", choices=["serve", "generate"], help="Action to perform")
    docs_parser.add_argument("--format", choices=["openapi", "html", "markdown"],
                             help="Documentation format", default="openapi")
    docs_parser.add_argument("--output", help="Output directory for generated docs")
    docs_parser.add_argument("--host", help="Host to serve docs on", default="localhost")
    docs_parser.add_argument("--port", help="Port to serve docs on", type=int, default=8000)
    docs_parser.add_argument("--module", help="Python module with service definitions")

    # Version command
    version_parser = subparsers.add_parser("version", help="Show version information")

    # Verbose flag
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose output")

    return parser.parse_args()


def get_version():
    """Get the current version of PIfunc."""
    try:
        return pkg_resources.get_distribution("pifunc").version
    except pkg_resources.DistributionNotFound:
        return "unknown (development version)"


def call_function(args):
    """Call a PIfunc function using the specified protocol."""
    function_name = args.function
    function_args = json.loads(args.args)
    protocol = args.protocol.lower()

    if protocol == "http":
        return call_http_function(args, function_name, function_args)
    elif protocol == "grpc":
        return call_grpc_function(args, function_name, function_args)
    else:
        logger.error(f"Protocol {protocol} is not supported by the CLI yet")
        return 1


def call_http_function(args, function_name, function_args):
    """Call a function using HTTP protocol."""
    # Determine port
    port = args.port or 8080

    # Determine path
    path = args.path or f"/api/{function_name}"

    # Build URL
    url = f"http://{args.host}:{port}{path}"

    logger.info(f"Calling {function_name} via HTTP {args.method} {url}")
    logger.info(f"Arguments: {json.dumps(function_args, indent=2)}")

    try:
        if args.method.upper() == "GET":
            response = requests.get(url, params=function_args, timeout=args.timeout)
        else:
            response = requests.post(url, json=function_args, timeout=args.timeout)

        response.raise_for_status()

        # Print result
        try:
            result = response.json()
            print(json.dumps(result, indent=2))
        except ValueError:
            print(response.text)

        return 0

    except requests.exceptions.RequestException as e:
        logger.error(f"HTTP request error: {str(e)}")
        if hasattr(e, 'response') and e.response:
            logger.error(f"Response: {e.response.text}")
        return 1


def call_grpc_function(args, function_name, function_args):
    """Call a function using gRPC protocol."""
    try:
        import grpc
        # We need to dynamically import the generated gRPC code
        # This is just a placeholder - the actual implementation would need to discover
        # and load the correct proto definitions
        logger.error("gRPC support in CLI requires generated stubs")
        logger.error("Please generate client code first: pifunc generate client --language python --protocol grpc")
        return 1
    except ImportError:
        logger.error("gRPC support requires the 'grpcio' package:")
        logger.error("pip install grpcio")
        return 1


def generate_client(args):
    """Generate client code for PIfunc services."""
    if args.language == "python":
        return generate_python_client(args)
    elif args.language in ["javascript", "typescript"]:
        return generate_js_client(args)
    else:
        logger.error(f"Language {args.language} is not supported yet")
        return 1


def generate_python_client(args):
    """Generate Python client code."""
    if not args.output:
        args.output = "pifunc_client.py"

    # Default port based on protocol
    if not args.port:
        if args.protocol == "http":
            args.port = 8080
        elif args.protocol == "grpc":
            args.port = 50051

    logger.info(f"Generating Python client for {args.protocol} protocol")
    logger.info(f"Output file: {args.output}")

    # Load service definitions if module is specified
    service_registry = {}
    if args.module:
        try:
            module = importlib.import_module(args.module)
            # Try to access the service registry if available
            if hasattr(module, "_SERVICE_REGISTRY"):
                service_registry = module._SERVICE_REGISTRY
            logger.info(f"Loaded service definitions from {args.module}")
        except (ImportError, AttributeError) as e:
            logger.warning(f"Could not load service definitions: {e}")

    # Generate client code
    client_code = generate_python_client_code(args, service_registry)

    # Write to file
    with open(args.output, "w") as f:
        f.write(client_code)

    logger.info(f"Client code written to {args.output}")
    return 0


def generate_python_client_code(args, service_registry):
    """Generate the actual Python client code."""
    protocol = args.protocol.lower()
    host = args.host
    port = args.port

    # Template for Python client
    template = f'''"""
PIfunc client generated by pifunc CLI.
Protocol: {protocol}
Server: {host}:{port}
"""

import json
import requests
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("pifunc_client")

class PiFuncClient:
    """Client for PIfunc services."""

    def __init__(self, base_url="{protocol}://{host}:{port}", protocol="{protocol}"):
        """Initialize the client."""
        self.base_url = base_url
        self.protocol = protocol
        self.setup_client()

    def setup_client(self):
        """Set up the client based on protocol."""
        if self.protocol == "http":
            # HTTP client is just requests library
            self._session = requests.Session()
        elif self.protocol == "grpc":
            # For gRPC, we would set up a channel and stubs
            # This is simplified - actual implementation would be more complex
            try:
                import grpc
                self._channel = grpc.insecure_channel(self.base_url)
                # Would need to import and set up stubs here
            except ImportError:
                logger.error("gRPC support requires the 'grpcio' package")
                raise

    def call(self, service_name: str, args: Optional[Dict[str, Any]] = None, **kwargs):
        """Call a service by name."""
        if args is None:
            args = dict()

        # Choose the right method based on protocol
        if self.protocol == "http":
            return self._call_http(service_name, args, **kwargs)
        elif self.protocol == "grpc":
            return self._call_grpc(service_name, args, **kwargs)
        else:
            raise ValueError(f"Unsupported protocol: {self.protocol}")

    def _call_http(self, service_name: str, args: Dict[str, Any], **kwargs):
        """Call a service via HTTP."""
        method = kwargs.get("method", "POST")
        path = kwargs.get("path", f"/api/{service_name}")
        url = f"{self.base_url}{path}"

        try:
            if method.upper() == "GET":
                response = self._session.get(url, params=args)
            else:
                response = self._session.post(url, json=args)

            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            logger.error(f"HTTP request error: {e}")
            return {"error": str(e)}

    def _call_grpc(self, service_name: str, args: Dict[str, Any], **kwargs):
        """Call a service via gRPC."""
        # This is simplified - actual implementation would need proper stub handling
        logger.error("gRPC calls are not fully implemented in this generated client")
        return {"error": "gRPC calls not implemented"}

    def close(self):
        """Close any open connections."""
        if self.protocol == "http":
            self._session.close()
        elif self.protocol == "grpc":
            # Close gRPC channel
            pass


# Generated service-specific methods based on registry
'''

    # Add service-specific methods if we have registry information
    if service_registry:
        template += "\n# Service-specific methods\n"

        for service_name, metadata in service_registry.items():
            # Only add methods for the selected protocol
            if protocol in metadata.get("protocols", []):
                # Get protocol-specific config
                protocol_config = metadata.get(protocol, {})

                # Get function signature
                signature = metadata.get("signature", {})
                parameters = signature.get("parameters", {})

                # Generate docstring
                docstring = f'"""{metadata.get("description", "")}\n\n'
                if parameters:
                    docstring += "Args:\n"
                    for param_name, param_info in parameters.items():
                        param_type = param_info.get("annotation", "Any").__name__
                        docstring += f"    {param_name}: {param_type}\n"
                docstring += '"""'

                # Generate method
                protocol_args = ""
                if protocol == "http":
                    path = protocol_config.get("path", f"/api/{service_name}")
                    method = protocol_config.get("method", "POST")
                    protocol_args = f'path="{path}", method="{method}"'

                params = ", ".join(parameters.keys())
                if params:
                    params = f", {params}"

                template += f'''
def {service_name}(self{params}):
    {docstring}
    return self.call("{service_name}", {{{", ".join(f'"{p}": {p}' for p in parameters.keys())}}}, {protocol_args})

PiFuncClient.{service_name} = {service_name}
'''

    return template


def generate_js_client(args):
    """Generate JavaScript/TypeScript client code."""
    if not args.output:
        ext = "ts" if args.language == "typescript" else "js"
        args.output = f"pifunc_client.{ext}"

    # JavaScript client generation is not implemented yet
    logger.error(f"{args.language.capitalize()} client generation is not implemented yet")
    return 1


def serve_docs(args):
    """Serve documentation for PIfunc services."""
    # Default port
    if not args.port:
        args.port = 8000

    logger.info(f"Starting documentation server on http://{args.host}:{args.port}")

    # For simplicity, we'll use FastAPI to serve OpenAPI docs
    try:
        from fastapi import FastAPI
        from fastapi.staticfiles import StaticFiles
        from fastapi.responses import RedirectResponse, HTMLResponse
        import uvicorn
    except ImportError:
        logger.error("Documentation server requires FastAPI and uvicorn:")
        logger.error("pip install fastapi uvicorn")
        return 1

    app = FastAPI(title="PIfunc Documentation")

    @app.get("/")
    async def root():
        return RedirectResponse(url="/docs")

    @app.get("/api/info")
    async def info():
        """API endpoint with basic PIfunc information."""
        return {
            "name": "PIfunc",
            "version": get_version(),
            "description": "Protocol Interface Functions"
        }

    # Load service definitions if module is specified
    if args.module:
        try:
            module = importlib.import_module(args.module)
            # Try to access the service registry if available
            if hasattr(module, "_SERVICE_REGISTRY"):
                service_registry = module._SERVICE_REGISTRY

                # Create endpoints for each service
                for service_name, metadata in service_registry.items():
                    # Add service info endpoint
                    @app.get(f"/api/services/{service_name}")
                    async def get_service_info():
                        return metadata
            else:
                logger.warning(f"No service registry found in {args.module}")
        except ImportError as e:
            logger.warning(f"Could not load module {args.module}: {e}")

    # Start server
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")
    return 0


def generate_docs(args):
    """Generate documentation for PIfunc services."""
    if not args.output:
        args.output = "docs"

    logger.info(f"Generating {args.format} documentation in {args.output}")

    # Ensure output directory exists
    os.makedirs(args.output, exist_ok=True)

    # Load service definitions if module is specified
    service_registry = {}
    if args.module:
        try:
            module = importlib.import_module(args.module)
            # Try to access the service registry if available
            if hasattr(module, "_SERVICE_REGISTRY"):
                service_registry = module._SERVICE_REGISTRY
                logger.info(f"Loaded service definitions from {args.module}")
            else:
                logger.warning(f"No service registry found in {args.module}")
        except ImportError as e:
            logger.warning(f"Could not load module {args.module}: {e}")

    # Generate documentation
    if args.format == "openapi":
        generate_openapi_docs(args, service_registry)
    elif args.format == "markdown":
        generate_markdown_docs(args, service_registry)
    elif args.format == "html":
        generate_html_docs(args, service_registry)

    logger.info(f"Documentation generated in {args.output}")
    return 0


def generate_openapi_docs(args, service_registry):
    """Generate OpenAPI documentation."""
    # This would create an OpenAPI spec file
    openapi_spec = {
        "openapi": "3.0.0",
        "info": {
            "title": "PIfunc API",
            "version": get_version(),
            "description": "API documentation for PIfunc services"
        },
        "paths": {}
    }

    # Add paths for HTTP services
    for service_name, metadata in service_registry.items():
        if "http" in metadata.get("protocols", []):
            http_config = metadata.get("http", {})
            path = http_config.get("path", f"/api/{service_name}")
            method = http_config.get("method", "POST").lower()

            # Create path entry if it doesn't exist
            if path not in openapi_spec["paths"]:
                openapi_spec["paths"][path] = {}

            # Add method to path
            openapi_spec["paths"][path][method] = {
                "summary": metadata.get("description", ""),
                "operationId": service_name,
                "responses": {
                    "200": {
                        "description": "Successful response",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object"
                                }
                            }
                        }
                    }
                }
            }

            # Add parameters or request body
            signature = metadata.get("signature", {})
            parameters = signature.get("parameters", {})

            if parameters:
                if method in ["get", "delete"]:
                    # For GET/DELETE, use query parameters
                    openapi_spec["paths"][path][method]["parameters"] = []
                    for param_name, param_info in parameters.items():
                        openapi_spec["paths"][path][method]["parameters"].append({
                            "name": param_name,
                            "in": "query",
                            "schema": {
                                "type": "string"  # Simplified - would need proper type mapping
                            }
                        })
                else:
                    # For POST/PUT/PATCH, use request body
                    openapi_spec["paths"][path][method]["requestBody"] = {
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        param_name: {
                                            "type": "string"  # Simplified
                                        } for param_name in parameters
                                    }
                                }
                            }
                        }
                    }

    # Write OpenAPI spec to file
    with open(os.path.join(args.output, "openapi.json"), "w") as f:
        json.dump(openapi_spec, f, indent=2)


def generate_markdown_docs(args, service_registry):
    """Generate Markdown documentation."""
    # This would create Markdown documentation
    docs = f"# PIfunc API Documentation\n\n"
    docs += f"Version: {get_version()}\n\n"

    # Add section for each service
    for service_name, metadata in service_registry.items():
        docs += f"## {service_name}\n\n"
        docs += f"{metadata.get('description', '')}\n\n"

        # Add protocol-specific information
        for protocol in metadata.get("protocols", []):
            protocol_config = metadata.get(protocol, {})
            docs += f"### {protocol.upper()}\n\n"

            if protocol == "http":
                path = protocol_config.get("path", f"/api/{service_name}")
                method = protocol_config.get("method", "POST")
                docs += f"- Path: `{path}`\n"
                docs += f"- Method: `{method}`\n\n"
            elif protocol == "websocket":
                event = protocol_config.get("event", service_name)
                docs += f"- Event: `{event}`\n\n"
            elif protocol == "mqtt":
                topic = protocol_config.get("topic", service_name)
                docs += f"- Topic: `{topic}`\n\n"

            # Add parameters
            signature = metadata.get("signature", {})
            parameters = signature.get("parameters", {})

            if parameters:
                docs += "#### Parameters\n\n"
                docs += "| Name | Type | Description |\n"
                docs += "| ---- | ---- | ----------- |\n"

                for param_name, param_info in parameters.items():
                    param_type = param_info.get("annotation", "Any").__name__
                    docs += f"| {param_name} | {param_type} | |\n"

                docs += "\n"

            # Add example
            docs += "#### Example\n\n"
            if protocol == "http":
                docs += "```bash\n"
                if method.upper() == "GET":
                    query_params = "&".join(f"{p}=value" for p in parameters)
                    docs += f"curl -X {method} \"{path}?{query_params}\"\n"
                else:
                    payload = {p: "value" for p in parameters}
                    docs += f"curl -X {method} {path} -H \"Content-Type: application/json\" -d '{json.dumps(payload)}'\n"
                docs += "```\n\n"

    # Write Markdown to file
    with open(os.path.join(args.output, "api.md"), "w") as f:
        f.write(docs)


def generate_html_docs(args, service_registry):
    """Generate HTML documentation."""
    # This would create HTML documentation
    # For simplicity, we'll just convert the Markdown to HTML
    try:
        import markdown
    except ImportError:
        logger.error("HTML documentation requires the 'markdown' package:")
        logger.error("pip install markdown")
        return

    # Generate Markdown first
    temp_args = argparse.Namespace(**vars(args))
    temp_args.format = "markdown"
    generate_markdown_docs(temp_args, service_registry)

    # Convert Markdown to HTML
    md_file = os.path.join(args.output, "api.md")
    with open(md_file, "r") as f:
        md_content = f.read()

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>PIfunc API Documentation</title>
        <style>
            body {{ font-family: Arial, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; }}
            th {{ background-color: #f2f2f2; }}
            code {{ background-color: #f5f5f5; padding: 2px 4px; border-radius: 4px; }}
            pre {{ background-color: #f5f5f5; padding: 10px; border-radius: 4px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        {markdown.markdown(md_content, extensions=['tables'])}
    </body>
    </html>
    """

    # Write HTML to file
    with open(os.path.join(args.output, "api.html"), "w") as f:
        f.write(html_content)


def main():
    """Main entry point for the CLI."""
    args = parse_args()

    # Set up logging
    level = logging.DEBUG if args.verbose else logging.INFO
    setup_logging(level)

    # Handle commands
    if args.command == "call":
        return call_function(args)
    elif args.command == "generate":
        return generate_client(args)
    elif args.command == "docs":
        if args.action == "serve":
            return serve_docs(args)
        else:  # generate
            return generate_docs(args)
    elif args.command == "version":
        print(f"PIfunc version: {get_version()}")
        return 0
    else:
        # No command provided, show help
        print("No command specified. Use --help for usage information.")
        return 1


if __name__ == "__main__":
    sys.exit(main())