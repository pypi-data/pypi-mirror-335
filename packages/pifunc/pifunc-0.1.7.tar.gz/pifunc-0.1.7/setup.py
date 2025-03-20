"""
pifunc - Convert markdown files into organized project structures with code files
"""
from setuptools import setup, find_packages

setup(
    name="pifunc",
    version="0.1.7",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "aiohttp>=3.8.0",
        "websockets>=10.0",
        "typing-extensions>=4.0.0",
        "redis>=4.0.0",
        "paho-mqtt>=1.6.0",
        "flask>=2.3.0",
        "requests>=2.31.0",
        "click>=8.1.0",
        "colorama>=0.4.6",
        "typing-extensions>=4.9.0",
        "pyyaml>=6.0.1",
        "fastapi>=0.110.0",
        "uvicorn>=0.27.0",
        "grpcio>=1.62.0",
        "grpcio-tools>=1.62.0",
    ],
    python_requires=">=3.11",
)
