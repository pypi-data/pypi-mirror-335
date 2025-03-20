# Contributing to PIfunc

Thank you for your interest in contributing to PIfunc! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## How Can I Contribute?

### Reporting Bugs

Before creating a bug report:

- Check the [existing issues](https://github.com/pifunc/pifunc/issues) to see if the problem has already been reported
- If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/pifunc/pifunc/issues/new/choose)

When reporting bugs, please include:

- A clear, descriptive title
- Exact steps to reproduce the problem
- Expected behavior and what actually happened
- Screenshots, if applicable
- Your environment (OS, Python version, PIfunc version)
- Any additional context

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues:

- Use a clear, descriptive title
- Provide a detailed description of the suggested enhancement
- Explain why this enhancement would be useful
- Include any relevant examples or mockups

### Your First Code Contribution

Unsure where to begin? Look for issues labeled `good first issue` or `help wanted`:

1. Fork the repository
2. Clone your fork locally
3. Set up the development environment
4. Make your changes
5. Test your changes
6. Submit a pull request

### Pull Requests

- Fill in the required PR template
- Reference any related issues
- Include screenshots or animated GIFs if needed
- Follow the coding standards (see below)
- Update documentation if needed
- Add tests for new features
- Ensure all tests pass

## Development Setup

1. Fork and clone the repository:
```bash
git clone https://github.com/pi-func/pifunc.git
cd pifunc
```

2. Set up a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=pifunc

# Run specific test file
pytest tests/test_http_adapter.py
```




1. Instalacja podstawowa:
```bash
pip install -r requirements.txt
```

2. Instalacja dla deweloperów:
```bash
pip install -r requirements-dev.txt
```

3. Uruchomienie testów:
```bash
tox
```

4. Instalacja pre-commit hooków:
```bash
pre-commit install
```

5. Sprawdzenie formatowania:
```bash
black .
flake8 .
mypy src/pifunc
isort .
```

Aktualizacja
```bash
pip install -e .
```

## RESTART

```bash
python -m venv venv && source venv/bin/activate && pip install -r requirements.txt -r requirements-dev.txt && python3 -m pip install -e .
```

## Issue

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-dev.txt
```            

## TEST

```bash
python3 -m pip install requests-mock && python3 -m pytest tests/ -vv
```

```bash
python3 -m pytest tests/ -v
```

## Coding Standards

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/) coding style
- Write docstrings according to [PEP 257](https://www.python.org/dev/peps/pep-0257/)
- Use type hints according to [PEP 484](https://www.python.org/dev/peps/pep-0484/)
- Format your code with [Black](https://black.readthedocs.io/)
- Sort imports with [isort](https://pycqa.github.io/isort/)
- Use meaningful variable, function, and class names
- Write clear, concise comments
- Keep functions small and focused on a single task

## Git Workflow

- Create a new branch for each feature or bugfix
- Use descriptive branch names (e.g., `feature/add-mqtt-qos`, `bugfix/http-headers`)
- Make small, focused commits with clear messages
- Keep your branch up to date with `main`
- Squash commits before merging if needed

## Commit Messages

Follow the [Conventional Commits](https://www.conventionalcommits.org/) specification:

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code changes that neither fix bugs nor add features
- `perf`: Performance improvements
- `test`: Adding or fixing tests
- `chore`: Changes to the build process or tools

Examples:
- `feat(http): add support for custom headers`
- `fix(grpc): resolve connection timeout issue`
- `docs: improve installation instructions`

## Adding Protocol Adapters

When adding a new protocol adapter:

1. Create a new file in `pifunc/adapters/`
2. Implement the `ProtocolAdapter` base class
3. Add tests for the new adapter
4. Update documentation to include the new protocol
5. Add examples demonstrating the new protocol

## Documentation

- Update the README.md if needed
- Add or update API documentation in docstrings
- If adding new features, update the appropriate docs files
- Consider adding examples to the examples directory

## Release Process

- The CI/CD pipeline will automatically publish to PyPI when a new tag is created
- Version bumps follow [Semantic Versioning](https://semver.org/)
- Releases are created by maintainers

## Questions?

If you have any questions or need help, feel free to:

- Open an issue for discussion
- Join our [Discord community](https://discord.gg/pifunc)
- Contact the maintainers directly

Thank you for contributing to PIfunc!