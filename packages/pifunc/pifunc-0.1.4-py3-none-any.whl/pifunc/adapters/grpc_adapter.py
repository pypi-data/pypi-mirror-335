# pifunc/adapters/grpc_adapter.py
import os
import sys
import time
import signal
import importlib
import inspect
import subprocess
import concurrent.futures
import grpc
import asyncio
from pathlib import Path
from typing import Any, Callable, Dict, List
import tempfile
from google.protobuf.json_format import MessageToDict, ParseDict
from grpc_reflection.v1alpha import reflection
from pifunc.adapters import ProtocolAdapter


class GRPCAdapter(ProtocolAdapter):
    """Adapter protokołu gRPC."""

    def __init__(self):
        self.server = None
        self.config = {}
        self.services = {}
        self.temp_dir = Path(tempfile.mkdtemp())
        self.proto_dir = self.temp_dir / 'proto'
        self.generated_dir = self.temp_dir / 'generated'
        self.proto_dir.mkdir(exist_ok=True)
        self.generated_dir.mkdir(exist_ok=True)

        # Dodajemy katalog wygenerowanych plików do ścieżki Pythona
        sys.path.append(str(self.generated_dir))

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter gRPC."""
        self.config = config
        self.max_workers = config.get("max_workers", 10)
        self.reflection = config.get("reflection", True)

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako usługę gRPC."""
        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację gRPC
        grpc_config = metadata.get("grpc", {})
        streaming = grpc_config.get("streaming", False)

        # Generujemy plik .proto
        self._generate_proto_file(func, service_name, streaming)

        # Kompilujemy plik .proto
        self._compile_proto_file(service_name)

        # Zapisujemy informacje o funkcji
        self.services[service_name] = {
            "function": func,
            "metadata": metadata,
            "streaming": streaming
        }

    def _generate_proto_file(self, func: Callable, service_name: str, streaming: bool) -> None:
        """Generuje plik .proto dla funkcji."""
        # Analizujemy sygnaturę funkcji
        signature = inspect.signature(func)

        # Przygotowujemy zawartość pliku .proto
        proto_content = f"""syntax = "proto3";

package pifunc;

service {service_name.capitalize()}Service {{
  rpc {service_name.capitalize()}("""

        # Dodajemy definicje wejścia/wyjścia z uwzględnieniem streamingu
        if streaming:
            proto_content += f"stream {service_name.capitalize()}Request) returns (stream {service_name.capitalize()}Response)"
        else:
            proto_content += f"{service_name.capitalize()}Request) returns ({service_name.capitalize()}Response)"

        proto_content += " {}\n}\n\n"

        # Dodajemy definicję wiadomości żądania
        proto_content += f"message {service_name.capitalize()}Request {{\n"

        for i, (param_name, param) in enumerate(signature.parameters.items(), 1):
            # Pobieramy typ parametru
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
            proto_type = self._get_proto_type(param_type)

            # Dodajemy pole do wiadomości
            proto_content += f"  {proto_type} {param_name} = {i};\n"

        proto_content += "}\n\n"

        # Dodajemy definicję wiadomości odpowiedzi
        proto_content += f"message {service_name.capitalize()}Response {{\n"

        # Pobieramy typ zwracany
        return_type = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None
        proto_type = self._get_proto_type(return_type)

        # Dodajemy pole do wiadomości
        proto_content += f"  {proto_type} result = 1;\n"
        proto_content += "}\n"

        # Zapisujemy plik .proto
        proto_file = self.proto_dir / f"{service_name}.proto"
        with open(proto_file, 'w') as f:
            f.write(proto_content)

    def _get_proto_type(self, python_type) -> str:
        """Konwertuje typ Pythona na typ protobuf."""
        if python_type is None:
            return "string"

        type_map = {
            int: "int32",
            float: "double",
            str: "string",
            bool: "bool",
            bytes: "bytes",
            list: "repeated string",
            dict: "map<string, string>"
        }

        return type_map.get(python_type, "string")

    def _compile_proto_file(self, service_name: str) -> None:
        """Kompiluje plik .proto do kodu Pythona."""
        proto_file = self.proto_dir / f"{service_name}.proto"

        try:
            # Tworzymy komendę do kompilacji
            cmd = [
                'python', '-m', 'grpc_tools.protoc',
                f'--proto_path={self.proto_dir}',
                f'--python_out={self.generated_dir}',
                f'--grpc_python_out={self.generated_dir}',
                str(proto_file)
            ]

            # Uruchamiamy kompilację
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            # Tworzymy plik __init__.py w katalogu z wygenerowanymi plikami
            init_file = self.generated_dir / '__init__.py'
            if not init_file.exists():
                init_file.touch()

        except subprocess.CalledProcessError as e:
            print(f"Błąd kompilacji pliku .proto: {e.stderr.decode()}")

    def start(self) -> None:
        """Uruchamia serwer gRPC."""
        port = self.config.get("port", 50051)
        host = self.config.get("host", "[::]")
        address = f"{host}:{port}"

        # Tworzymy serwer gRPC
        self.server = grpc.server(
            concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers)
        )

        # Rejestrujemy usługi
        service_names = []
        for service_name, service_info in self.services.items():
            # Importujemy wygenerowane moduły
            pb2_module = importlib.import_module(f"{service_name}_pb2")
            pb2_grpc_module = importlib.import_module(f"{service_name}_pb2_grpc")

            # Tworzymy serwis
            service_class = self._create_service_class(
                service_name,
                service_info["function"],
                service_info["streaming"],
                pb2_module,
                pb2_grpc_module
            )

            # Rejestrujemy serwis
            service_names.append(f"pifunc.{service_name.capitalize()}Service")
            servicer_add_method = getattr(
                pb2_grpc_module,
                f"add_{service_name.capitalize()}ServiceServicer_to_server"
            )
            servicer_add_method(service_class(), self.server)

        # Dodajemy serwis reflection
        if self.reflection:
            service_names.append(reflection.SERVICE_NAME)
            reflection.enable_server_reflection(service_names, self.server)

        # Uruchamiamy serwer
        self.server.add_insecure_port(address)
        self.server.start()

        print(f"Serwer gRPC uruchomiony na {address}")

    def _create_service_class(self, service_name, func, streaming, pb2_module, pb2_grpc_module):
        """Tworzy klasę implementującą usługę gRPC."""
        servicer_class_name = f"{service_name.capitalize()}ServiceServicer"
        base_servicer_class = getattr(pb2_grpc_module, servicer_class_name)
        request_class = getattr(pb2_module, f"{service_name.capitalize()}Request")
        response_class = getattr(pb2_module, f"{service_name.capitalize()}Response")

        # Tworzymy klasę serwisu
        class ServiceImplementation(base_servicer_class):

            def __getattribute__(self, name):
                # Jeśli metoda to nasza usługa RPC
                if name == f"{service_name.capitalize()}":
                    if streaming:
                        # Implementacja streamingu
                        async def streaming_method(request_iterator, context):
                            try:
                                # Przetwarzamy stream wejściowy
                                async def process_input_stream():
                                    for request in request_iterator:
                                        # Konwertujemy request na słownik argumentów
                                        kwargs = MessageToDict(
                                            request,
                                            preserving_proto_field_name=True
                                        )
                                        # Przekazujemy do funkcji
                                        result = func(**kwargs)

                                        # Jeśli funkcja zwraca coroutine, czekamy na wynik
                                        if asyncio.iscoroutine(result):
                                            result = await result

                                        # Zwracamy wynik jako stream
                                        yield response_class(result=str(result))

                                # Zwracamy generator
                                return process_input_stream()

                            except Exception as e:
                                context.set_code(grpc.StatusCode.INTERNAL)
                                context.set_details(str(e))
                                raise

                        return streaming_method
                    else:
                        # Implementacja standardowej metody
                        def unary_method(request, context):
                            try:
                                # Konwertujemy request na słownik argumentów
                                kwargs = MessageToDict(
                                    request,
                                    preserving_proto_field_name=True
                                )

                                # Wywołujemy funkcję
                                result = func(**kwargs)

                                # Jeśli funkcja zwraca coroutine, czekamy na wynik
                                if asyncio.iscoroutine(result):
                                    # Tworzymy nową pętlę asyncio
                                    loop = asyncio.new_event_loop()
                                    asyncio.set_event_loop(loop)
                                    result = loop.run_until_complete(result)
                                    loop.close()

                                # Zwracamy wynik
                                return response_class(result=str(result))

                            except Exception as e:
                                context.set_code(grpc.StatusCode.INTERNAL)
                                context.set_details(str(e))
                                raise

                        return unary_method

                # W przeciwnym razie zwracamy oryginalny atrybut
                return super().__getattribute__(name)

        return ServiceImplementation

    def stop(self) -> None:
        """Zatrzymuje serwer gRPC."""
        if self.server:
            self.server.stop(0)
            print("Serwer gRPC zatrzymany")

            # Czyścimy pliki tymczasowe
            import shutil
            try:
                shutil.rmtree(self.temp_dir)
            except:
                pass