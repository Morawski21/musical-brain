"""
Integration tests for CRUD services.

These tests require a running Neo4j instance and will modify the database.
Run with: pytest tests/test_services.py -v
"""

import pytest
import pytest_asyncio
from datetime import datetime

from musical_brain.database import DatabaseManager, db
from musical_brain.services import (
    create_node, get_node, update_node, delete_node, 
    list_nodes, count_nodes, initialize_schema
)
from musical_brain.models import Album, Artist, Genre, AlbumType


# Test database configuration
TEST_DB_URI = "bolt://localhost:7687"
TEST_DB_USER = "neo4j"
TEST_DB_PASSWORD = "password"


@pytest_asyncio.fixture(scope="session")
async def db_connection():
    """Set up test database connection."""
    # Use the global db instance
    await db.connect(TEST_DB_URI, TEST_DB_USER, TEST_DB_PASSWORD)
    
    # Initialize schema
    await initialize_schema()
    
    yield db
    
    # Cleanup: remove all test nodes
    await db.run_query("MATCH (n) WHERE n.id STARTS WITH 'test-' DELETE n")
    await db.disconnect()


@pytest_asyncio.fixture
async def clean_db(db_connection):
    """Clean test data before each test."""
    # Remove any existing test nodes
    await db_connection.run_query("MATCH (n) WHERE n.id STARTS WITH 'test-' DELETE n")
    yield
    # Cleanup after test
    await db_connection.run_query("MATCH (n) WHERE n.id STARTS WITH 'test-' DELETE n")


class TestSchemaInitialization:
    """Test schema creation and constraints."""

    @pytest.mark.asyncio
    async def test_initialize_schema(self, db_connection):
        """Test schema initialization creates constraints and indexes."""
        # Schema should already be initialized by fixture
        # Test that we can call it again without errors
        await initialize_schema()
        
        # Verify constraints exist by trying to create duplicate IDs
        album_data = {"title": "Test Album", "album_type": "LP"}
        await create_node("Album", album_data)
        
        # This should work (different node, auto-generated ID)
        await create_node("Album", album_data)


class TestAlbumCRUD:
    """Test CRUD operations for Album nodes."""

    @pytest.mark.asyncio
    async def test_create_album(self, clean_db):
        """Test creating an album."""
        album_data = {
            "title": "Test Album",
            "album_type": "LP",
            "release_year": 2023,
            "review_score": 4.5,
            "review_notes": "Excellent progressive rock album"
        }
        
        result = await create_node("Album", album_data)
        
        assert result["title"] == "Test Album"
        assert result["album_type"] == "LP"
        assert result["release_year"] == 2023
        assert result["review_score"] == 4.5
        assert result["review_notes"] == "Excellent progressive rock album"
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result

    @pytest.mark.asyncio
    async def test_get_album(self, clean_db):
        """Test retrieving an album by ID."""
        # Create an album first
        album_data = {"title": "Get Test Album", "album_type": "EP"}
        created = await create_node("Album", album_data)
        album_id = created["id"]
        
        # Retrieve it
        result = await get_node("Album", album_id)
        
        assert result is not None
        assert result["id"] == album_id
        assert result["title"] == "Get Test Album"
        assert result["album_type"] == "EP"

    @pytest.mark.asyncio
    async def test_get_nonexistent_album(self, clean_db):
        """Test retrieving a non-existent album returns None."""
        result = await get_node("Album", "test-nonexistent-id")
        assert result is None

    @pytest.mark.asyncio
    async def test_update_album(self, clean_db):
        """Test updating an album."""
        # Create an album first
        album_data = {"title": "Update Test Album", "album_type": "LP"}
        created = await create_node("Album", album_data)
        album_id = created["id"]
        
        # Update it
        updates = {
            "review_score": 3.8,
            "review_notes": "Updated review notes",
            "release_year": 2022
        }
        result = await update_node("Album", album_id, updates)
        
        assert result is not None
        assert result["id"] == album_id
        assert result["title"] == "Update Test Album"  # Unchanged
        assert result["review_score"] == 3.8
        assert result["review_notes"] == "Updated review notes"
        assert result["release_year"] == 2022
        assert "updated_at" in result
        # updated_at should be different from created_at
        assert result["updated_at"] != result["created_at"]

    @pytest.mark.asyncio
    async def test_update_nonexistent_album(self, clean_db):
        """Test updating a non-existent album returns None."""
        updates = {"review_score": 4.0}
        result = await update_node("Album", "test-nonexistent-id", updates)
        assert result is None

    @pytest.mark.asyncio
    async def test_update_album_empty_updates(self, clean_db):
        """Test updating album with empty updates."""
        # Create an album first
        album_data = {"title": "Empty Update Test", "album_type": "Single"}
        created = await create_node("Album", album_data)
        album_id = created["id"]
        
        # Update with empty dict
        result = await update_node("Album", album_id, {})
        
        assert result is not None
        assert result["id"] == album_id
        assert result["title"] == "Empty Update Test"

    @pytest.mark.asyncio
    async def test_delete_album(self, clean_db):
        """Test deleting an album."""
        # Create an album first
        album_data = {"title": "Delete Test Album", "album_type": "Compilation"}
        created = await create_node("Album", album_data)
        album_id = created["id"]
        
        # Delete it
        success = await delete_node("Album", album_id)
        assert success is True
        
        # Verify it's gone
        result = await get_node("Album", album_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_delete_nonexistent_album(self, clean_db):
        """Test deleting a non-existent album returns False."""
        success = await delete_node("Album", "test-nonexistent-id")
        assert success is False

    @pytest.mark.asyncio
    async def test_list_albums(self, clean_db):
        """Test listing albums with pagination."""
        # Create multiple albums
        albums = []
        for i in range(5):
            album_data = {
                "title": f"List Test Album {i}",
                "album_type": "LP"
            }
            album = await create_node("Album", album_data)
            albums.append(album)
        
        # List all albums
        result = await list_nodes("Album", limit=10)
        
        # Should get all 5 albums, newest first
        assert len(result) == 5
        assert result[0]["title"] == "List Test Album 4"  # Newest first
        assert result[4]["title"] == "List Test Album 0"  # Oldest last
        
        # Test pagination
        first_page = await list_nodes("Album", limit=2, offset=0)
        second_page = await list_nodes("Album", limit=2, offset=2)
        
        assert len(first_page) == 2
        assert len(second_page) == 2
        assert first_page[0]["title"] != second_page[0]["title"]

    @pytest.mark.asyncio
    async def test_count_albums(self, clean_db):
        """Test counting albums."""
        # Initially should be 0
        count = await count_nodes("Album")
        assert count == 0
        
        # Create some albums
        for i in range(3):
            album_data = {"title": f"Count Test Album {i}", "album_type": "EP"}
            await create_node("Album", album_data)
        
        # Should now be 3
        count = await count_nodes("Album")
        assert count == 3


class TestArtistCRUD:
    """Test CRUD operations for Artist nodes."""

    @pytest.mark.asyncio
    async def test_create_artist(self, clean_db):
        """Test creating an artist."""
        artist_data = {
            "name": "Test Artist",
            "country": "USA",
            "formed_year": 1990,
            "notes": "Great progressive rock band"
        }
        
        result = await create_node("Artist", artist_data)
        
        assert result["name"] == "Test Artist"
        assert result["country"] == "USA"
        assert result["formed_year"] == 1990
        assert result["notes"] == "Great progressive rock band"
        assert "id" in result
        assert "created_at" in result
        # Artists don't get updated_at on creation
        assert "updated_at" not in result

    @pytest.mark.asyncio
    async def test_artist_no_updated_at_on_update(self, clean_db):
        """Test that artists don't get updated_at timestamp on update."""
        # Create an artist
        artist_data = {"name": "Update Test Artist"}
        created = await create_node("Artist", artist_data)
        artist_id = created["id"]
        
        # Update it
        updates = {"country": "Canada", "notes": "Updated notes"}
        result = await update_node("Artist", artist_id, updates)
        
        assert result is not None
        assert result["country"] == "Canada"
        assert result["notes"] == "Updated notes"
        # Should not have updated_at
        assert "updated_at" not in result


class TestGenreCRUD:
    """Test CRUD operations for Genre nodes."""

    @pytest.mark.asyncio
    async def test_create_genre(self, clean_db):
        """Test creating a genre."""
        genre_data = {
            "name": "Progressive Rock",
            "description": "Complex rock music with lengthy compositions"
        }
        
        result = await create_node("Genre", genre_data)
        
        assert result["name"] == "Progressive Rock"
        assert result["description"] == "Complex rock music with lengthy compositions"
        assert "id" in result
        # Genres don't get timestamps
        assert "created_at" not in result
        assert "updated_at" not in result


class TestCRUDWithPydanticModels:
    """Test CRUD operations work with Pydantic models."""

    @pytest.mark.asyncio
    async def test_create_album_from_pydantic_model(self, clean_db):
        """Test creating album using Pydantic model data."""
        album = Album(
            title="Pydantic Test Album",
            album_type=AlbumType.LP,
            release_year=2023,
            review_score=4.2
        )
        
        # Convert to dict for database (excluding None fields)
        album_data = album.model_dump(exclude_none=True, exclude={"id", "created_at", "updated_at"})
        
        result = await create_node("Album", album_data)
        
        assert result["title"] == "Pydantic Test Album"
        assert result["album_type"] == "LP"
        assert result["release_year"] == 2023
        assert result["review_score"] == 4.2

    @pytest.mark.asyncio
    async def test_convert_db_result_to_pydantic_model(self, clean_db):
        """Test converting database result back to Pydantic model."""
        # Create album in database
        album_data = {
            "title": "Convert Test Album",
            "album_type": "EP",
            "review_score": 3.5
        }
        db_result = await create_node("Album", album_data)
        
        # Convert back to Pydantic model
        album = Album.model_validate(db_result)
        
        assert album.title == "Convert Test Album"
        assert album.album_type == AlbumType.EP
        assert album.review_score == 3.5
        assert album.id == db_result["id"]
        assert album.created_at is not None
        assert album.updated_at is not None