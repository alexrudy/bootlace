
# Set up the virtual environment based on the direnv convention
# https://direnv.net/docs/legacy.html#virtualenv
virtual_env :=  justfile_directory() / ".direnv/python-3.11/bin"
export PATH := virtual_env + ":" + env('PATH')

[private]
prepare:
    pip install --quiet --upgrade pip
    pip install --quiet pip-tools pip-compile-multi

sync: prepare
    pip-compile-multi --use-cache
    pip-sync requirements/dev.txt
    pip install -e .
    tox --notest

# Run tests
test:
    pytest

# Run all tests
test-all:
    tox

# Run lints
lint:
    flake8

# Run mypy
mypy:
    mypy

# Build docs
docs:
    cd docs && make html

# Clean up
clean:
    rm -rf dist/* *.egg-info
    rm -rf docs/_build

# Clean more stuff
clean-all: clean
    rm -rf .direnv
    rm -rf .venv
    rm -rf .tox
    rm -rf .mypy_cache .pytest_cache
    rm -rf docs/api
    rm -rf .coverage htmlcov
