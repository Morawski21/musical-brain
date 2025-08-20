"""
Simple Neo4j database connection for Musical Brain.
"""

import logging
from typing import Optional

from neo4j import AsyncGraphDatabase, AsyncDriver


class DatabaseManager:
    """Simple Neo4j database manager."""

    def __init__(self):
        self.driver: Optional[AsyncDriver] = None
        self.logger = logging.getLogger(__name__)

    async def connect(
        self,
        uri: str = "bolt://localhost:7687",
        user: str = "neo4j",
        password: str = "password",
    ):
        """Connect to Neo4j database."""
        try:
            self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))
            # Test the connection
            await self.driver.verify_connectivity()
            self.logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            self.logger.error(f"Failed to connect to Neo4j: {e}")
            raise

    async def disconnect(self):
        """Close the database connection."""
        if self.driver:
            await self.driver.close()
            self.logger.info("Disconnected from Neo4j")

    async def run_query(self, query: str, parameters: dict = None) -> list:
        """Run a simple Cypher query and return results."""
        if not self.driver:
            raise RuntimeError("Not connected to database. Call connect() first.")

        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()

    async def test_connection(self) -> bool:
        """Test if database is working."""
        try:
            result = await self.run_query("RETURN 'Hello Neo4j!' as message")
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False


# Global database instance
db = DatabaseManager()
