# Instalacja frameworka
pip install pifunc

# 1. Uruchomienie wszystkich usług z pliku
pifunc serve simple_service.py

# 2. Uruchomienie usług tylko przez wybrane protokoły
pifunc serve simple_service.py --protocols grpc http

# 3. Konfiguracja portów dla różnych protokołów
pifunc serve simple_service.py --grpc-port 50051 --http-port 8080 --mqtt-broker mqtt://localhost:1883

# 4. Uruchomienie z hot-reload
pifunc serve simple_service.py --watch

# 5. Uruchomienie usług z katalogu (wykrywa wszystkie pliki z usługami)
pifunc serve ./services

# 6. Uruchomienie w trybie produkcyjnym
pifunc serve simple_service.py --env production --workers 4

# 7. Generowanie dokumentacji dla usług
pifunc docs --output ./docs

# 8. Testowanie funkcji przez różne protokoły
pifunc call add --protocol http --args '{"a": 5, "b": 3}'
pifunc call add --protocol grpc --args 'a=5 b=3'
pifunc call add --protocol mqtt --args '{"a": 5, "b": 3}'

# 9. Generowanie klientów dla różnych języków i protokołów
pifunc generate client --language javascript --protocols http websocket
pifunc generate client --language python --protocols grpc mqtt

# 10. Uruchomienie interfejsu zarządzania
pifunc dashboard