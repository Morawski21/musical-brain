# Use PowerShell on Windows
set shell := ["powershell.exe", "-c"]

# Setup project
setup:
    uv sync
    uv run pre-commit install

# Code quality
lint:
    uv run ruff check .
    uv run ruff format .
   
# Testing
test:
    uv run pytest

# Clean up cache files
clean:
    rm -rf **/__pycache__
    rm -rf .pytest_cache
    rm -rf .ruff_cache