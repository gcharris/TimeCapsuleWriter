# Contributing to TimeCapsuleWriter

Thank you for your interest in contributing to TimeCapsuleWriter! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please treat all contributors and users with respect. We aim to foster an inclusive and welcoming community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with the following information:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Environment information (OS, Python version, dependencies)
- Screenshots if applicable

### Suggesting Features

We welcome feature suggestions! Please create an issue with:

- A clear, descriptive title
- Detailed description of the proposed feature
- Any relevant context or examples
- Possible implementation approaches (optional)

### Pull Requests

1. Fork the repository
2. Create a new branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests to ensure they pass (`pytest`)
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Coding Standards

- Follow PEP 8 style guidelines
- Add type hints where appropriate
- Write docstrings for all functions, classes, and modules
- Keep functions small and focused on a single task
- Add tests for new functionality

## Development Setup

1. Clone your fork of the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run tests to ensure everything is working:
   ```bash
   pytest
   ```

## Testing

- Write tests for all new functionality
- Run the test suite before submitting a PR:
  ```bash
  pytest
  ```
- For coverage reports:
  ```bash
  pytest --cov=. --cov-report=term
  ```

## Documentation

- Update documentation when changing functionality
- Ensure examples are up to date
- Follow the existing documentation style

## Questions?

If you have questions about contributing, feel free to open an issue for clarification.

Thank you for contributing to TimeCapsuleWriter!
