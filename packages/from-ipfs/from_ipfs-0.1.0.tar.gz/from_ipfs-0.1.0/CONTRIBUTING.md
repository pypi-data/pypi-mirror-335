# Contributing to from_ipfs

Thank you for your interest in contributing to `from_ipfs`! This document provides guidelines and instructions for contributing to this project.

## Development Setup

1. Clone the repository:

```bash
git clone https://github.com/alexbakers/from_ipfs.git
cd from-ipfs
```

2. Create a virtual environment and install development dependencies:

```bash
uv venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

## Development Workflow

1. Create a new branch for your changes:

```bash
git checkout -b feature/your-feature-name
```

2. Make your changes and ensure tests pass:

```bash
# Run tests
pytest

# Run linters
black .
isort .
ruff check .
```

3. Commit your changes with a descriptive message:

```bash
git commit -m "Add feature X"
```

4. Push your branch to GitHub:

```bash
git push origin feature/your-feature-name
```

5. Open a pull request on GitHub.

## Testing

- All new features should include appropriate tests.
- All tests must pass before a pull request can be merged.
- Run tests with pytest:

```bash
pytest
```

## Code Style

This project uses:

- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [ruff](https://github.com/charliermarsh/ruff) for linting

Configuration for these tools is in `pyproject.toml`.

## Pull Request Process

1. Update the README.md or documentation with details of changes if appropriate.
2. Update the tests to reflect your changes.
3. Your PR should pass all CI checks.
4. A maintainer will review your PR and may request changes.
5. Once approved, a maintainer will merge your PR.

## Release Process

1. Update version in `from_ipfs/__init__.py`.
2. Update CHANGELOG.md.
3. Create a new release on GitHub.
4. Publish to PyPI:

```bash
uv build
uv upload dist/*
```

## License

By contributing to `from_ipfs`, you agree that your contributions will be licensed under the project's MIT License.
