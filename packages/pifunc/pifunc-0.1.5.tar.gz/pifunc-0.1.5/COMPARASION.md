# Porównanie z podobnymi rozwiązaniami

Istnieje kilka podobnych rozwiązań umożliwiających tworzenie usług dostępnych przez różne protokoły komunikacyjne. Oto najważniejsze z nich wraz z kluczowymi różnicami:

## 1. FastAPI + gRPC

**FastAPI** to popularny framework do tworzenia API HTTP, który można połączyć z gRPC.

**Różnice:**
- FastAPI skupia się głównie na HTTP/REST, a gRPC jest dodawany osobno
- Wymaga pisania dwóch oddzielnych implementacji lub dodatkowej warstwy abstrakcji
- Nie ma natywnego wsparcia dla MQTT czy WebSocket (trzeba używać dodatkowych bibliotek)
- Wymaga więcej kodu boilerplate w porównaniu do PIfunc

## 2. NestJS (JavaScript/TypeScript)

**NestJS** to framework dla Node.js obsługujący wiele protokołów.

**Różnice:**
- Dostępny tylko dla JavaScript/TypeScript, nie dla Pythona
- Używa koncepcji kontrolerów i providerów (bardziej rozbudowana architektura)
- Wymaga więcej konfiguracji i boilerplate
- Ma bardziej rozbudowany ekosystem i większą liczbę funkcji
- Obsługuje HTTP, WebSocket, gRPC, ale MQTT wymaga dodatkowych modułów

## 3. Spring Cloud (Java)

**Spring Cloud** to zestaw narzędzi dla Javy do budowania systemów rozproszonych.

**Różnice:**
- Znacznie bardziej rozbudowany i skomplikowany
- Przeznaczony głównie dla dużych systemów enterprise
- Wymaga dużej ilości konfiguracji i konwencji
- Natywnie obsługuje HTTP i gRPC, inne protokoły wymagają dodatkowych modułów
- Dostępny tylko dla Javy, nie dla Pythona

## 4. Micronaut (Java/Kotlin/Groovy)

**Micronaut** to framework do budowania mikrousług i aplikacji serverless.

**Różnice:**
- Obsługuje HTTP, gRPC i funkcje serverless
- Brak natywnego wsparcia dla MQTT i WebSocket
- Używa kompilacji AOT (Ahead-Of-Time) do przyspieszenia startu
- Bardziej skomplikowana architektura niż PIfunc
- Dostępny dla JVM, nie dla Pythona

## 5. Moleculer (JavaScript/Node.js)

**Moleculer** to framework do tworzenia mikrousług.

**Różnice:**
- Skupia się na komunikacji między usługami, a nie różnych protokołach dla klientów
- Używa własnego protokołu komunikacyjnego, choć może być rozszerzony
- Dostępny tylko dla JavaScript, nie dla Pythona
- Bardziej zaawansowany w zarządzaniu usługami (service discovery, load balancing)
- Wymaga większej ilości konfiguracji

## 6. Zappa (Python)

**Zappa** to narzędzie do wdrażania aplikacji Python jako funkcje serverless.

**Różnice:**
- Skupia się na wdrażaniu aplikacji WSGI/ASGI w AWS Lambda
- Głównie do aplikacji HTTP, bez natywnego wsparcia dla innych protokołów
- Nie zapewnia jednolitego API dla różnych protokołów
- Bardziej skupiony na wdrażaniu niż na rozwoju

## 7. tRPC (TypeScript)

**tRPC** to system RPC dla TypeScript z end-to-end typowaniem.

**Różnice:**
- Tylko dla TypeScript, brak wsparcia dla Pythona
- Skupia się na jednym protokole z silnym typowaniem
- Nie obsługuje MQTT, WebSocket czy gRPC
- Bardzo lekki i prosty w porównaniu do innych rozwiązań

## 8. API Gateway + Lambda (AWS)

**Wzorzec wykorzystujący AWS API Gateway i Lambda Functions**.

**Różnice:**
- Wymaga infrastruktury AWS
- Może obsługiwać HTTP, WebSocket i integracje z innymi usługami AWS
- Większy koszt utrzymania i zarządzania
- Brak natywnego wsparcia dla gRPC czy MQTT
- Wymaga napisania oddzielnych funkcji Lambda dla każdego endpointu

## Główne przewagi frameworka PIfunc

1. **Prostota** - Znacznie mniej kodu boilerplate i konfiguracji niż większość konkurencyjnych rozwiązań
2. **Jednolite API** - Ten sam dekorator `@service` dla wszystkich protokołów
3. **Natywne wsparcie dla wielu protokołów** - gRPC, HTTP, MQTT, WebSocket i GraphQL bez dodatkowych modułów
4. **Python-first** - Zaprojektowany specjalnie dla Pythona, wykorzystujący adnotacje typów i dekoratory
5. **Automatyczna konwersja typów** - Nie wymaga ręcznego mapowania między formatami danych
6. **Łatwa konfiguracja** - Prosta konfiguracja poprzez słowniki Pythona

PIfunc łączy zalety wielu rozwiązań, oferując prostotę podobną do FastAPI, wsparcie dla wielu protokołów jak NestJS, ale z naciskiem na minimalny kod boilerplate i prostotę konfiguracji, co jest unikalne wśród istniejących rozwiązań, szczególnie dla ekosystemu Pythona.