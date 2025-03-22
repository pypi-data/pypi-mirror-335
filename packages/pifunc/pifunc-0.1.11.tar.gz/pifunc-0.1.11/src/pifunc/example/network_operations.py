import socket
import requests
import json
import urllib.parse
from typing import Dict, Any, Optional, Union
import ssl
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import ftplib
import asyncio
import aiohttp
import websockets

class HTTPClient:
    """Simple HTTP client implementation."""
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, endpoint: str, params: Optional[Dict] = None) -> requests.Response:
        """Send GET request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.get(url, params=params, timeout=self.timeout)

    def post(self, endpoint: str, data: Any) -> requests.Response:
        """Send POST request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.post(url, json=data, timeout=self.timeout)

    def put(self, endpoint: str, data: Any) -> requests.Response:
        """Send PUT request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.put(url, json=data, timeout=self.timeout)

    def delete(self, endpoint: str) -> requests.Response:
        """Send DELETE request."""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        return self.session.delete(url, timeout=self.timeout)

class TCPServer:
    """Simple TCP server implementation."""
    def __init__(self, host: str = 'localhost', port: int = 8000):
        self.host = host
        self.port = port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def start(self, callback):
        """Start TCP server."""
        self.socket.bind((self.host, self.port))
        self.socket.listen(1)
        print(f"Server listening on {self.host}:{self.port}")
        
        try:
            while True:
                client, address = self.socket.accept()
                callback(client, address)
        finally:
            self.socket.close()

class SSLContext:
    """SSL context manager for secure connections."""
    @staticmethod
    def create_ssl_context(cert_file: str, key_file: str) -> ssl.SSLContext:
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.load_cert_chain(certfile=cert_file, keyfile=key_file)
        return context

class EmailSender:
    """Email sender using SMTP."""
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password

    def send_email(self, to_email: str, subject: str, body: str, is_html: bool = False):
        """Send email using SMTP."""
        msg = MIMEMultipart()
        msg['From'] = self.username
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'html' if is_html else 'plain'))

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)

class FTPClient:
    """FTP client implementation."""
    def __init__(self, host: str, username: str, password: str):
        self.host = host
        self.username = username
        self.password = password
        self.ftp = ftplib.FTP(host)
        self.ftp.login(username, password)

    def upload_file(self, local_path: str, remote_path: str):
        """Upload file to FTP server."""
        with open(local_path, 'rb') as file:
            self.ftp.storbinary(f'STOR {remote_path}', file)

    def download_file(self, remote_path: str, local_path: str):
        """Download file from FTP server."""
        with open(local_path, 'wb') as file:
            self.ftp.retrbinary(f'RETR {remote_path}', file.write)

    def close(self):
        """Close FTP connection."""
        self.ftp.quit()

class WebSocketClient:
    """WebSocket client implementation."""
    async def connect(self, uri: str, on_message):
        """Connect to WebSocket server."""
        async with websockets.connect(uri) as websocket:
            while True:
                message = await websocket.recv()
                await on_message(message)

class AsyncHTTPClient:
    """Asynchronous HTTP client implementation."""
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()

    async def get(self, url: str) -> Dict:
        """Async GET request."""
        async with self.session.get(url) as response:
            return await response.json()

    async def post(self, url: str, data: Dict) -> Dict:
        """Async POST request."""
        async with self.session.post(url, json=data) as response:
            return await response.json()

def url_encode(data: Union[str, Dict]) -> str:
    """URL encode string or dictionary."""
    if isinstance(data, dict):
        return urllib.parse.urlencode(data)
    return urllib.parse.quote(data)

def url_decode(data: str) -> Union[str, Dict]:
    """URL decode string or query string."""
    if '=' in data:
        return dict(urllib.parse.parse_qsl(data))
    return urllib.parse.unquote(data)

def is_port_open(host: str, port: int, timeout: float = 2.0) -> bool:
    """Check if a port is open on the given host."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(timeout)
    try:
        result = sock.connect_ex((host, port))
        return result == 0
    finally:
        sock.close()
