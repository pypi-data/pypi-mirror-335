
# pyodide_backend

This is the backend for pyodide exercises.
It wraps pythonwhat and manages processes, providing just an interface to run init, run code, and run submit.
It tries to be as similar as possible to `pythonbackend`.

## Installing

```bash
# Runtime dependencies
pip install .
# Build dependencies
pip install '.[build]'
# Test dependencies
pip install '.[test]'
```

## Building

```bash
python -m build --wheel
```

## Running tests

```bash
pytest
```
