import pytest
from musical_brain.database import DatabaseManager


class TestDatabaseManager:
    """Test suite for DatabaseManager functionality."""

    @pytest.mark.asyncio
    async def test_database_manager_initialization(self):
        """Test DatabaseManager can be initialized properly."""
        db = DatabaseManager()
        assert db is not None
        assert db.driver is None
        assert db.logger is not None

    @pytest.mark.asyncio
    async def test_run_query_requires_connection(self):
        """Test that run_query raises error when not connected."""
        db = DatabaseManager()

        with pytest.raises(RuntimeError, match="Not connected to database"):
            await db.run_query("RETURN 1")

    @pytest.mark.asyncio
    async def test_disconnect_when_not_connected(self):
        """Test that disconnect can be called safely when not connected."""
        db = DatabaseManager()

        # Should not raise an error
        await db.disconnect()

    @pytest.mark.asyncio
    async def test_test_connection_when_not_connected(self):
        """Test that test_connection returns False when not connected."""
        db = DatabaseManager()

        result = await db.test_connection()
        assert result is False
