"""
Musical Brain - A simple music knowledge graph API.
"""

import logging
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from musical_brain.database import db

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Musical Brain...")
    try:
        await db.connect()
        logger.info("Musical Brain startup completed")
    except Exception as e:
        logger.error(f"Failed to start Musical Brain: {e}")
        raise

    yield

    # Shutdown
    logger.info("Shutting down Musical Brain...")
    try:
        await db.disconnect()
        logger.info("Musical Brain shutdown completed")
    except Exception as e:
        logger.error(f"Error during shutdown: {e}")


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
    logger.debug("Health check requested")
    db_ok = await db.test_connection()
    status = "healthy" if db_ok else "unhealthy"
    logger.info(f"Health check result: {status}")
    return {
        "status": status,
        "database": "connected" if db_ok else "disconnected",
    }


@app.get("/test-neo4j")
async def test_neo4j():
    """Simple test to see if Neo4j is working."""
    logger.debug("Neo4j test requested")
    try:
        result = await db.run_query(
            "RETURN 'Neo4j is working!' as message, datetime() as timestamp"
        )
        logger.info("Neo4j test successful")
        return {"success": True, "data": result}
    except Exception as e:
        logger.error(f"Neo4j test failed: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
