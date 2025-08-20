"""
Musical Brain - A simple music knowledge graph API.
"""

from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from musical_brain.database import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Starting Musical Brain...")
    await db.connect()

    yield

    # Shutdown
    print("Shutting down Musical Brain...")
    await db.disconnect()


app = FastAPI(
    title="Musical Brain",
    description="A simple music knowledge graph API",
    version="0.1.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Welcome message."""
    return {"message": "Welcome to Musical Brain!"}


@app.get("/health")
async def health_check():
    """Check if the API and database are working."""
    db_ok = await db.test_connection()
    return {
        "status": "healthy" if db_ok else "unhealthy",
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/test-neo4j")
async def test_neo4j():
    """Simple test to see if Neo4j is working."""
    try:
        result = await db.run_query(
            "RETURN 'Neo4j is working!' as message, datetime() as timestamp"
        )
        return {"success": True, "data": result}
    except Exception as e:
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
