"""
Unit tests for Pydantic models.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from musical_brain.models import Album, Artist, Genre, AlbumType


class TestAlbumModel:
    """Test suite for Album model."""

    def test_album_creation_minimal(self):
        """Test creating album with minimal required fields."""
        album = Album(
            title="Test Album",
            album_type=AlbumType.LP
        )
        assert album.title == "Test Album"
        assert album.album_type == AlbumType.LP
        assert album.id is None
        assert album.created_at is None

    def test_album_creation_full(self):
        """Test creating album with all fields."""
        now = datetime.utcnow()
        album = Album(
            id="test-id",
            title="Test Album",
            album_type=AlbumType.EP,
            release_year=2023,
            review_score=4.5,
            review_notes="Great album!",
            review_date=now,
            created_at=now,
            updated_at=now
        )
        assert album.id == "test-id"
        assert album.title == "Test Album"
        assert album.album_type == AlbumType.EP
        assert album.release_year == 2023
        assert album.review_score == 4.5
        assert album.review_notes == "Great album!"
        assert album.review_date == now
        assert album.created_at == now
        assert album.updated_at == now

    def test_album_title_validation(self):
        """Test album title validation."""
        # Empty title should fail
        with pytest.raises(ValidationError):
            Album(title="", album_type=AlbumType.LP)
        
        # Very long title should fail
        with pytest.raises(ValidationError):
            Album(title="x" * 201, album_type=AlbumType.LP)

    def test_album_year_validation(self):
        """Test album year validation."""
        # Year too early should fail
        with pytest.raises(ValidationError):
            Album(title="Test", album_type=AlbumType.LP, release_year=1800)
        
        # Year too late should fail
        with pytest.raises(ValidationError):
            Album(title="Test", album_type=AlbumType.LP, release_year=2031)
        
        # Valid years should pass
        album = Album(title="Test", album_type=AlbumType.LP, release_year=2000)
        assert album.release_year == 2000

    def test_album_score_validation(self):
        """Test album score validation."""
        # Score too low should fail
        with pytest.raises(ValidationError):
            Album(title="Test", album_type=AlbumType.LP, review_score=-0.1)
        
        # Score too high should fail
        with pytest.raises(ValidationError):
            Album(title="Test", album_type=AlbumType.LP, review_score=5.1)
        
        # Valid scores should pass
        album = Album(title="Test", album_type=AlbumType.LP, review_score=3.7)
        assert album.review_score == 3.7

    def test_album_type_enum(self):
        """Test album type enumeration."""
        # Test all valid types
        for album_type in AlbumType:
            album = Album(title="Test", album_type=album_type)
            assert album.album_type == album_type
        
        # Invalid type should fail
        with pytest.raises(ValidationError):
            Album(title="Test", album_type="Invalid")


class TestArtistModel:
    """Test suite for Artist model."""

    def test_artist_creation_minimal(self):
        """Test creating artist with minimal required fields."""
        artist = Artist(name="Test Artist")
        assert artist.name == "Test Artist"
        assert artist.id is None
        assert artist.country is None
        assert artist.formed_year is None
        assert artist.notes is None
        assert artist.created_at is None

    def test_artist_creation_full(self):
        """Test creating artist with all fields."""
        now = datetime.utcnow()
        artist = Artist(
            id="test-id",
            name="Test Artist",
            country="USA",
            formed_year=1990,
            notes="Great band",
            created_at=now
        )
        assert artist.id == "test-id"
        assert artist.name == "Test Artist"
        assert artist.country == "USA"
        assert artist.formed_year == 1990
        assert artist.notes == "Great band"
        assert artist.created_at == now

    def test_artist_name_validation(self):
        """Test artist name validation."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            Artist(name="")
        
        # Very long name should fail
        with pytest.raises(ValidationError):
            Artist(name="x" * 201)

    def test_artist_year_validation(self):
        """Test artist formed year validation."""
        # Year too early should fail
        with pytest.raises(ValidationError):
            Artist(name="Test", formed_year=1700)
        
        # Year too late should fail
        with pytest.raises(ValidationError):
            Artist(name="Test", formed_year=2031)
        
        # Valid year should pass
        artist = Artist(name="Test", formed_year=1980)
        assert artist.formed_year == 1980

    def test_artist_country_validation(self):
        """Test artist country validation."""
        # Very long country should fail
        with pytest.raises(ValidationError):
            Artist(name="Test", country="x" * 101)
        
        # Valid country should pass
        artist = Artist(name="Test", country="Canada")
        assert artist.country == "Canada"


class TestGenreModel:
    """Test suite for Genre model."""

    def test_genre_creation_minimal(self):
        """Test creating genre with minimal required fields."""
        genre = Genre(name="Rock")
        assert genre.name == "Rock"
        assert genre.id is None
        assert genre.description is None

    def test_genre_creation_full(self):
        """Test creating genre with all fields."""
        genre = Genre(
            id="test-id",
            name="Progressive Rock",
            description="Complex rock music with lengthy compositions"
        )
        assert genre.id == "test-id"
        assert genre.name == "Progressive Rock"
        assert genre.description == "Complex rock music with lengthy compositions"

    def test_genre_name_validation(self):
        """Test genre name validation."""
        # Empty name should fail
        with pytest.raises(ValidationError):
            Genre(name="")
        
        # Very long name should fail
        with pytest.raises(ValidationError):
            Genre(name="x" * 101)

    def test_model_from_attributes_config(self):
        """Test that models can be created from objects with attributes."""
        # Simulate Neo4j record-like object
        class MockRecord:
            def __init__(self):
                self.id = "test-id"
                self.name = "Test Genre"
                self.description = "Test description"
        
        record = MockRecord()
        genre = Genre.model_validate(record)
        assert genre.id == "test-id"
        assert genre.name == "Test Genre"
        assert genre.description == "Test description"