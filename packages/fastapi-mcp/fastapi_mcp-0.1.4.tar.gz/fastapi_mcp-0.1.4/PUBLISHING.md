# Publishing FastAPI-MCP to PyPI

This guide explains how to publish the FastAPI-MCP package to PyPI.

## Prerequisites

1. Create a PyPI account at https://pypi.org/account/register/
2. Generate an API token at https://pypi.org/manage/account/token/

## Setup

1. Copy the template and create your `.pypirc` file:

```bash
cp .pypirc.template ~/.pypirc
```

2. Edit the file with your actual PyPI token:

```bash
nano ~/.pypirc
```

3. Make sure the file is only readable by you:

```bash
chmod 600 ~/.pypirc
```

## Building the Package

1. Install the build tools:

```bash
pip install build twine
```

2. Build the package:

```bash
python -m build
```

This will create both source distribution and wheel files in the `dist/` directory.

## Testing the Distribution

Before uploading to PyPI, it's good practice to verify the package:

```bash
twine check dist/*
```

## Publishing to TestPyPI (Recommended first step)

TestPyPI is a separate instance of the Python Package Index that allows you to test your package:

```bash
twine upload --repository testpypi dist/*
```

Then install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ fastapi-mcp
```

## Publishing to PyPI

Once you're confident everything works:

```bash
twine upload dist/*
```

## Verifying the Installation

```bash
pip install fastapi-mcp
```

## Updating the Package

1. Update the version number in:
   - `pyproject.toml`
   - `setup.py`
   - `fastapi_mcp/__init__.py`
   - `CHANGELOG.md`

2. Build and upload the new version following the steps above.

## Semantic Versioning

Follow these guidelines for version numbers:

- **MAJOR** version when you make incompatible API changes
- **MINOR** version when you add functionality in a backward-compatible manner
- **PATCH** version when you make backward-compatible bug fixes

For example: 1.0.0 -> 1.0.1 (patch) -> 1.1.0 (minor) -> 2.0.0 (major) 