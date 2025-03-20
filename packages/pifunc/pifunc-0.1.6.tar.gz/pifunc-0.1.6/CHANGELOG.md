# Changelog

All notable changes to this project will be documented in this file.

## [0.1.6] - 2025-03-19

## [0.1.6] - 2025-03-19

### Added
- Changes in calculator/Dockerfile
- Changes in calculator/README.md
- Changes in calculator/client.py
- Changes in calculator/docker-compose.yml
- Changes in calculator/requirements.txt
- Changes in calculator/service.py
- Changes in calculator/static/index.html


## [0.1.5] - 2025-03-19

### Added
- Changes in src/pifunc/example/README.md
- Changes in src/pifunc/example/data_service/client.py
- Changes in src/pifunc/example/data_service/docker-compose.yml
- Changes in src/pifunc/example/data_service/service.py
- Changes in src/pifunc/example/docker-compose.yml
- Changes in src/pifunc/example/math_service/Dockerfile
- Changes in src/pifunc/example/math_service/client.py
- Changes in src/pifunc/example/math_service/docker-compose.yml
- Changes in src/pifunc/example/math_service/service.py
- Changes in src/pifunc/example/string_service/Dockerfile
- Changes in src/pifunc/example/string_service/client.py
- Changes in src/pifunc/example/string_service/docker-compose.yml
- Changes in src/pifunc/example/string_service/service.py

## [0.1.4] - 2025-03-19

### Added
- Changes in PROTOCOLS.md
- Changes in src/pifunc/example/basic_calculator.py
- Changes in src/pifunc/example/data_structure_functions.py
- Changes in src/pifunc/example/database_operations.py
- Changes in src/pifunc/example/docker-compose-basic.yml
- Changes in src/pifunc/example/docker-compose-microservices.yml
- Changes in src/pifunc/example/docker-compose-monitoring.yml
- Changes in src/pifunc/example/file_operations.py
- Changes in src/pifunc/example/math_functions.py
- Changes in src/pifunc/example/network_operations.py
- Changes in src/pifunc/example/protocol_math_functions.py
- Changes in src/pifunc/example/string_functions.py
- Changes in src/pifunc/adapters/amqp_adapter.py
- Changes in src/pifunc/adapters/zeromq_adapter.py
- Changes in src/pifunc/example/clients_examples.py
- Changes in src/pifunc/example/multi_protocol_service.py

### Changed
- Changes in src/pifunc/example/clients_examples.py


## [0.1.3] - 2025-03-20

### Changed
- Enhanced HTTP adapter with improved type handling and parameter conversion
- Enhanced MQTT adapter with better message processing and error handling
- Added detailed logging for both HTTP and MQTT adapters
- Fixed dict parameter handling in service functions
- Improved error messages and debugging capabilities

### Fixed
- Fixed type conversion issues with dict parameters in HTTP and MQTT adapters
- Fixed MQTT message handling and response routing
- Resolved issues with async function handling in both adapters

### Documentation
- Added detailed logging messages for better debugging
- Improved error messages for better problem diagnosis
- Added debug-level logging for request/response payloads

## [0.1.2] - 2025-03-19

### Added
- Initial release of PIfunc with multi-protocol support
- Core service decorator implementation for HTTP, gRPC, MQTT, WebSocket, and GraphQL protocols
- CLI tool for service management and interaction
- Type-safe function exposure across protocols
- Hot reload capability for development
- Automatic API documentation generation
- Protocol-specific configuration options
- Example implementations and usage guides
- Development tools and scripts:
  - Pre-commit hooks for code quality
  - Test automation scripts
  - Version management utilities
  - Build and publish workflows

### Changed
- Updated project structure for better modularity
- Enhanced HTTP and MQTT adapters with improved error handling
- Refined CLI interface for better user experience

### Documentation
- Added comprehensive README with installation and usage guides
- Included detailed API documentation
- Added contribution guidelines
- Created example code snippets for common use cases

### Testing
- Added comprehensive test suite:
  - CLI functionality tests
  - Service decorator tests
  - HTTP adapter tests
  - Integration tests across protocols
- Implemented test fixtures and utilities
- Added async testing support
- Added cross-protocol testing scenarios
