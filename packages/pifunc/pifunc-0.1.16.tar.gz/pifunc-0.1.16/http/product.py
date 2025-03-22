from random import randint, choice
from string import ascii_letters

from pifunc import service, client, run_services


@service(
    http={"path": "/api/products", "method": "POST"}
)
def create_product(product: dict) -> dict:
    """Create a new product."""
    return {
        "id": product["id"],
        "name": product["name"],
        "price": product["price"],
        "in_stock": product.get("in_stock", True)
    }


@service(
    http={"path": "/", "method": "GET"}
)
def hello() -> dict:
    return {
        "description": "Create a new product API",
        "path": "/api/products",
        "url": "http://127.0.0.1:8080/api/products/",
        "method": "POST",
        "protocol": "HTTP",
        "version": "1.1",
        "example_data": {
            "id": "1",
            "name": "test",
            "price": "10",
            "in_stock": True
        },
    }


@client(
    http={"path": "/api/products", "method": "POST"}
)
@service(
    cron={"interval": "1m"}
)
def generate_product() -> dict:
    """Generate a random product every minute."""
    product = {
        "id": str(randint(1000, 9999)),
        "name": ''.join(choice(ascii_letters) for i in range(8)),
        "price": str(randint(10, 100)),
        "in_stock": True
    }
    print(f"Generating random product: {product}")
    return product


if __name__ == "__main__":
    # Rozwiązanie problemu z importem klienta
    import sys
    import os

    # Monkeypatching importu klienta w __init__.py
    import types

    sys.modules['pifunc_client'] = types.ModuleType('pifunc_client')
    sys.modules['pifunc_client'].PiFuncClient = type('PiFuncClient', (), {
        '__init__': lambda self, base_url='', protocol='': None,
        'call': lambda self, service_name, args=None, **kwargs: None,
        'close': lambda self: None
    })

    # Uruchomienie z ograniczonymi protokołami
    run_services(
        http={"port": 8080},
        cron={"check_interval": 1},
        protocols=["http", "cron"],
        watch=True
    )