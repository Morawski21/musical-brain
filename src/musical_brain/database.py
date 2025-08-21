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
            self.logger.error("Attempted to run query without database connection")
            raise RuntimeError("Not connected to database. Call connect() first.")

        self.logger.debug(f"Executing query: {query[:100]}{'...' if len(query) > 100 else ''}")
        try:
            async with self.driver.session() as session:
                result = await session.run(query, parameters or {})
                data = await result.data()
                self.logger.debug(f"Query returned {len(data)} records")
                return data
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise

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
