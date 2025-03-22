# Changelog

All notable changes to this project will be documented in this file.

## [0.1.2] - 2025-03-21

### Changed
- Changes in mqtt/mqtt.py
- Changes in zeromq/CHANGELOG.md
- Changes in zeromq/README.md
- Changes in zeromq/changelog.py
- Changes in zeromq/checker.sh
- Changes in zeromq/service.py
- Changes in zeromq/test.sh

## [0.1.1] - 2025-03-21

### Changed
- Changes in mqtt/mqtt.py



## [0.1.0] - 2025-03-21

### Changed
- Changes in zeromq/CHANGELOG.md
- Changes in zeromq/README.md
- Changes in zeromq/changelog.py
- Changes in zeromq/checker.sh
- Changes in zeromq/service.py
- Changes in zeromq/test.sh

### Fixed

1. **Fixed ZeroMQ Adapter**:
   - Corrected the structure and removed bugs
   - Added proper environment variable support
   - Improved error handling and logging
   - Completed the PUB/SUB implementation

2. **Created a ZeroMQ Service Example**:
   - Added multiple service patterns (REQ/REP, PUB/SUB, PUSH/PULL)
   - Used environment variables for configuration
   - Added different service types for demonstration

3. **Created a Test Client Script**:
   - Implemented tests for all service patterns
   - Used Python within bash for proper JSON handling
   - Added clear output formatting and error handling

4. **Updated the .env File**:
   - Added all necessary configuration for both API and ZeroMQ services
   - 
