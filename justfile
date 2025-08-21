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
    uv run pytest -v

# Run only unit tests (no database required)
test-unit:
    uv run pytest tests/unit/ -v

# Run only integration tests (requires running Neo4j)
test-integration:
    uv run pytest tests/integration/ -v

# Run tests with coverage report
test-coverage:
    uv run pytest --cov=musical_brain --cov-report=html -v

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