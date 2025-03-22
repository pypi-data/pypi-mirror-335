# pifunc/adapters/graphql_adapter.py
import json
import inspect
import asyncio
import threading
from typing import Any, Callable, Dict, List, Optional, Type, get_type_hints
from pathlib import Path
import dataclasses
from aiohttp import web
from pifunc.adapters import ProtocolAdapter

# Importy GraphQL
import graphql
from graphql import (
    GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLString,
    GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLList,
    GraphQLArgument, GraphQLNonNull, GraphQLInputObjectType,
    GraphQLInputField, GraphQLScalarType, GraphQLEnumType
)


class GraphQLAdapter(ProtocolAdapter):
    """Adapter protokołu GraphQL."""

    def __init__(self):
        self.config = {}
        self.query_fields = {}
        self.mutation_fields = {}
        self.schema = None
        self.app = None
        self.runner = None
        self.site = None
        self.server_thread = None

        # Przechowujemy zarejestrowane typy
        self.registered_types = {
            int: GraphQLInt,
            float: GraphQLFloat,
            str: GraphQLString,
            bool: GraphQLBoolean,
        }

        # Przechowujemy typy wejściowe i wyjściowe dla dataclasses
        self.input_types = {}
        self.output_types = {}

    def setup(self, config: Dict[str, Any]) -> None:
        """Konfiguruje adapter GraphQL."""
        self.config = config

    def register_function(self, func: Callable, metadata: Dict[str, Any]) -> None:
        """Rejestruje funkcję jako pole GraphQL."""
        service_name = metadata.get("name", func.__name__)

        # Pobieramy konfigurację GraphQL
        graphql_config = metadata.get("graphql", {})
        field_name = graphql_config.get("field_name", service_name)
        description = graphql_config.get("description", func.__doc__ or "")
        is_mutation = graphql_config.get("is_mutation", False)

        # Analizujemy sygnaturę funkcji
        signature = inspect.signature(func)

        # Przygotowujemy argumenty GraphQL
        args = {}
        for param_name, param in signature.parameters.items():
            # Pobieramy typ parametru
            param_type = param.annotation if param.annotation != inspect.Parameter.empty else None
            graphql_type = self._get_graphql_type(param_type)

            # Dodajemy argument do pola
            if param.default == inspect.Parameter.empty:
                # Argument wymagany
                graphql_type = GraphQLNonNull(graphql_type)

            args[param_name] = GraphQLArgument(
                type=graphql_type,
                description=f"Argument {param_name}"
            )

        # Pobieramy typ zwracany
        return_type = signature.return_annotation if signature.return_annotation != inspect.Parameter.empty else None
        return_graphql_type = self._get_graphql_type(return_type)

        # Tworzymy pole GraphQL
        field = GraphQLField(
            type=return_graphql_type,
            args=args,
            resolve=lambda obj, info, **kwargs: self._resolve_field(func, kwargs),
            description=description
        )

        # Zapisujemy pole w odpowiedniej kolekcji
        if is_mutation:
            self.mutation_fields[field_name] = field
        else:
            self.query_fields[field_name] = field

    def _get_graphql_type(self, python_type) -> Any:
        """Konwertuje typ Pythona na typ GraphQL."""
        # Sprawdzamy, czy typ jest już zarejestrowany
        if python_type in self.registered_types:
            return self.registered_types[python_type]

        # Obsługa typów podstawowych
        if python_type is None:
            return GraphQLString

        # Obsługa list
        if hasattr(python_type, "__origin__") and python_type.__origin__ is list:
            item_type = python_type.__args__[0]
            return GraphQLList(self._get_graphql_type(item_type))

        # Obsługa słowników - konwertujemy na JSON
        if hasattr(python_type, "__origin__") and python_type.__origin__ is dict:
            return GraphQLString

        # Obsługa typów niestandardowych (dataclasses)
        if dataclasses.is_dataclass(python_type):
            # Sprawdzamy, czy typ wyjściowy już istnieje
            if python_type.__name__ in self.output_types:
                return self.output_types[python_type.__name__]

            # Tworzymy nowy typ wyjściowy
            fields = {}
            for field_name, field_type in get_type_hints(python_type).items():
                fields[field_name] = GraphQLField(
                    type=self._get_graphql_type(field_type),
                    description=f"Field {field_name}"
                )

            output_type = GraphQLObjectType(
                name=python_type.__name__,
                fields=fields,
                description=f"Type for {python_type.__name__}"
            )

            # Zapisujemy typ wyjściowy
            self.output_types[python_type.__name__] = output_type

            # Tworzymy typ wejściowy
            input_fields = {}
            for field_name, field_type in get_type_hints(python_type).items():
                input_fields[field_name] = GraphQLInputField(
                    type=self._get_graphql_type(field_type),
                    description=f"Input field {field_name}"
                )

            input_type = GraphQLInputObjectType(
                name=f"{python_type.__name__}Input",
                fields=input_fields,
                description=f"Input type for {python_type.__name__}"
            )

            # Zapisujemy typ wejściowy
            self.input_types[python_type.__name__] = input_type

            return output_type

        # Domyślnie zwracamy string
        return GraphQLString

    def _resolve_field(self, func: Callable, kwargs: Dict[str, Any]) -> Any:
        """Wykonuje funkcję i zwraca wynik dla pola GraphQL."""
        try:
            # Wywołujemy funkcję
            result = func(**kwargs)

            # Obsługujemy coroutines
            if asyncio.iscoroutine(result):
                # Tworzymy nową pętlę asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(result)
                loop.close()

            return result

        except Exception as e:
            # Przekazujemy wyjątek do GraphQL
            raise graphql.GraphQLError(str(e))

    def _build_schema(self) -> GraphQLSchema:
        """Buduje schemat GraphQL na podstawie zarejestrowanych funkcji."""
        # Tworzymy typ Query
        query_type = None
        if self.query_fields:
            query_type = GraphQLObjectType(
                name="Query",
                fields=self.query_fields
            )

        # Tworzymy typ Mutation
        mutation_type = None
        if self.mutation_fields:
            mutation_type = GraphQLObjectType(
                name="Mutation",
                fields=self.mutation_fields
            )

        # Tworzymy schemat
        schema = GraphQLSchema(
            query=query_type,
            mutation=mutation_type
        )

        return schema

    async def _handle_graphql_request(self, request):
        """Obsługuje żądanie GraphQL."""
        # Pobieramy dane żądania
        if request.method == "POST":
            data = await request.json()
        else:
            data = dict(request.query)

        # Pobieramy zapytanie
        query = data.get("query")
        variables = data.get("variables", {})
        operation_name = data.get("operationName")

        if not query:
            return web.json_response(
                {"errors": [{"message": "Missing query"}]},
                status=400
            )

        # Wykonujemy zapytanie
        result = await graphql.graphql(
            schema=self.schema,
            source=query,
            variable_values=variables,
            operation_name=operation_name
        )

        # Przygotowujemy odpowiedź
        response = {}
        if result.errors:
            response["errors"] = [{"message": str(error)} for error in result.errors]
        response["data"] = result.data

        return web.json_response(response)

    async def _handle_graphiql_request(self, request):
        """Obsługuje żądanie GraphiQL (interfejs przeglądarkowy)."""
        graphiql_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>GraphiQL</title>
            <link href="https://cdnjs.cloudflare.com/ajax/libs/graphiql/1.7.2/graphiql.min.css" rel="stylesheet" />
            <script src="https://cdnjs.cloudflare.com/ajax/libs/react/17.0.2/umd/react.production.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/react-dom/17.0.2/umd/react-dom.production.min.js"></script>
            <script src="https://cdnjs.cloudflare.com/ajax/libs/graphiql/1.7.2/graphiql.min.js"></script>
        </head>
        <body style="margin: 0; width: 100%; height: 100%; overflow: hidden;">
            <div id="graphiql" style="height: 100vh;"></div>
            <script>
                const fetcher = params => {
                    return fetch('/graphql', {
                        method: 'post',
                        headers: {
                            'Accept': 'application/json',
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(params),
                    }).then(response => response.json());
                };

                ReactDOM.render(
                    React.createElement(GraphiQL, { fetcher: fetcher }),
                    document.getElementById('graphiql')
                );
            </script>
        </body>
        </html>
        """

        return web.Response(
            text=graphiql_html,
            content_type="text/html"
        )

    async def _run_server(self):
        """Uruchamia serwer GraphQL."""
        host = self.config.get("host", "0.0.0.0")
        port = self.config.get("port", 8082)
        playground = self.config.get("playground", True)

        # Tworzymy aplikację aiohttp
        self.app = web.Application()

        # Dodajemy endpoint GraphQL
        self.app.router.add_post("/graphql", self._handle_graphql_request)
        self.app.router.add_get("/graphql", self._handle_graphql_request)

        # Dodajemy endpoint GraphiQL, jeśli playground jest włączony
        if playground:
            self.app.router.add_get("/", self._handle_graphiql_request)

        # Uruchamiamy serwer
        self.runner = web.AppRunner(self.app)
        await self.runner.setup()

        self.site = web.TCPSite(self.runner, host, port)
        await self.site.start()

        print(f"Serwer GraphQL uruchomiony na http://{host}:{port}/graphql")
        if playground:
            print(f"Interfejs GraphiQL dostępny na http://{host}:{port}/")

    def _server_thread_func(self):
        """Funkcja wątku serwera."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            loop.run_until_complete(self._run_server())
            loop.run_forever()
        except Exception as e:
            print(f"Błąd serwera GraphQL: {e}")
        finally:
            loop.close()

    def start(self) -> None:
        """Uruchamia serwer GraphQL."""
        # Budujemy schemat
        self.schema = self._build_schema()

        # Uruchamiamy serwer w osobnym wątku
        self.server_thread = threading.Thread(target=self._server_thread_func)
        self.server_thread.daemon = True
        self.server_thread.start()

    def stop(self) -> None:
        """Zatrzymuje serwer GraphQL."""
        # Zatrzymujemy serwer
        if self.site and self.runner:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(self.site.stop())
                loop.run_until_complete(self.runner.cleanup())
            finally:
                loop.close()

            print("Serwer GraphQL zatrzymany")