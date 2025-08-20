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

# Start Neo4j database
db:
    docker-compose up -d neo4j

# Start FastAPI development server
serve:
    uv run uvicorn musical_brain.app:app --reload --host 0.0.0.0 --port 8000

# Stop all services
stop:
    docker-compose down

# Clean up cache files
clean:
    rm -rf **/__pycache__
    rm -rf .pytest_cache
    rm -rf .ruff_cache