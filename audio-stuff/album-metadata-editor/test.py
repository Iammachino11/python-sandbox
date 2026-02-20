"""
Unit tests for Album Metadata Editor

Run with: pytest tests/test_editor.py -v
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from album_metadata_editor import (
    AlbumMetadataEditor,
    MetadataStats,
    AlbumMetadata,
    MissingMetadata
)


class TestAlbumMetadataEditor:
    """Test suite for AlbumMetadataEditor class."""
    
    def test_initialization_default_params(self):
        """Test editor initialization with default parameters."""
        editor = AlbumMetadataEditor()
        
        assert editor.rename_files is False
        assert editor.interactive is True
        assert editor.auto_number is False
        assert isinstance(editor.stats, MetadataStats)
    
    def test_initialization_custom_params(self):
        """Test editor initialization with custom parameters."""
        editor = AlbumMetadataEditor(
            rename_files=True,
            interactive=False,
            auto_number=True,
            verbose=True
        )
        
        assert editor.rename_files is True
        assert editor.interactive is False
        assert editor.auto_number is True
    
    def test_find_audio_files_empty_directory(self):
        """Test finding audio files in an empty directory."""
        editor = AlbumMetadataEditor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            audio_files = editor.find_audio_files(tmpdir)
            assert len(audio_files) == 0
    
    def test_find_audio_files_invalid_directory(self):
        """Test finding audio files with invalid directory."""
        editor = AlbumMetadataEditor()
        
        with pytest.raises(FileNotFoundError):
            editor.find_audio_files("/nonexistent/directory")
    
    def test_find_cover_art_found(self):
        """Test finding cover art when it exists."""
        editor = AlbumMetadataEditor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a dummy cover.jpg
            cover_path = Path(tmpdir) / "cover.jpg"
            cover_path.touch()
            
            result = editor.find_cover_art(tmpdir)
            
            assert result is not None
            assert result.name == "cover.jpg"
    
    def test_find_cover_art_not_found(self):
        """Test finding cover art when it doesn't exist."""
        editor = AlbumMetadataEditor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            result = editor.find_cover_art(tmpdir)
            assert result is None
    
    def test_load_cover_art_success(self):
        """Test loading cover art successfully."""
        editor = AlbumMetadataEditor()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            cover_path = Path(tmpdir) / "cover.jpg"
            test_data = b"fake image data"
            cover_path.write_bytes(test_data)
            
            result = editor.load_cover_art(cover_path)
            
            assert result == test_data
    
    def test_load_cover_art_failure(self):
        """Test loading cover art with invalid file."""
        editor = AlbumMetadataEditor()
        
        cover_path = Path("/nonexistent/cover.jpg")
        result = editor.load_cover_art(cover_path)
        
        assert result is None
    
    def test_generate_filename_basic(self):
        """Test filename generation with basic inputs."""
        editor = AlbumMetadataEditor()
        
        filepath = Path("/test/song.mp3")
        filename = editor.generate_filename(filepath, "5", "My Song Title")
        
        assert filename == "05 - My Song Title.mp3"
    
    def test_generate_filename_with_slash_tracknumber(self):
        """Test filename generation with slash in track number."""
        editor = AlbumMetadataEditor()
        
        filepath = Path("/test/song.mp3")
        filename = editor.generate_filename(filepath, "3/12", "Another Song")
        
        assert filename == "03 - Another Song.mp3"
    
    def test_generate_filename_special_characters(self):
        """Test filename generation with special characters in title."""
        editor = AlbumMetadataEditor()
        
        filepath = Path("/test/song.flac")
        filename = editor.generate_filename(
            filepath,
            "1",
            "Song: With/Special\\Characters?"
        )
        
        # Should remove invalid characters
        assert ":" not in filename
        assert "/" not in filename
        assert "\\" not in filename
        assert "?" not in filename
    
    def test_supported_formats_constant(self):
        """Test that supported formats are defined."""
        assert '.mp3' in AlbumMetadataEditor.SUPPORTED_FORMATS
        assert '.flac' in AlbumMetadataEditor.SUPPORTED_FORMATS
    
    def test_default_cover_names_constant(self):
        """Test that default cover names are defined."""
        assert 'cover.jpg' in AlbumMetadataEditor.DEFAULT_COVER_NAMES
        assert 'cover.png' in AlbumMetadataEditor.DEFAULT_COVER_NAMES


class TestMetadataStats:
    """Test suite for MetadataStats dataclass."""
    
    def test_stats_initialization(self):
        """Test MetadataStats initialization."""
        stats = MetadataStats()
        
        assert stats.total_files == 0
        assert stats.updated == 0
        assert stats.renamed == 0
        assert stats.failed == 0
        assert stats.skipped == 0
    
    def test_stats_increment(self):
        """Test incrementing stats counters."""
        stats = MetadataStats()
        
        stats.total_files = 10
        stats.updated = 8
        stats.renamed = 5
        stats.failed = 1
        stats.skipped = 1
        
        assert stats.total_files == 10
        assert stats.updated == 8
        assert stats.renamed == 5
        assert stats.failed == 1
        assert stats.skipped == 1


class TestAlbumMetadata:
    """Test suite for AlbumMetadata dataclass."""
    
    def test_metadata_initialization_empty(self):
        """Test AlbumMetadata initialization with no data."""
        metadata = AlbumMetadata()
        
        assert metadata.album_name is None
        assert metadata.year is None
        assert metadata.album_artist is None
        assert metadata.cover_data is None
        assert metadata.cover_path is None
    
    def test_metadata_initialization_with_data(self):
        """Test AlbumMetadata initialization with data."""
        metadata = AlbumMetadata(
            album_name="Test Album",
            year="2024",
            album_artist="Test Artist",
            cover_data=b"image data",
            cover_path="/path/to/cover.jpg"
        )
        
        assert metadata.album_name == "Test Album"
        assert metadata.year == "2024"
        assert metadata.album_artist == "Test Artist"
        assert metadata.cover_data == b"image data"
        assert metadata.cover_path == "/path/to/cover.jpg"


class TestMissingMetadata:
    """Test suite for MissingMetadata dataclass."""
    
    def test_missing_metadata_initialization(self):
        """Test MissingMetadata initialization."""
        missing = MissingMetadata()
        
        assert missing.album is False
        assert missing.year is False
        assert missing.album_artist is False
        assert missing.tracknumber is False
        assert missing.title is False
    
    def test_missing_metadata_all_missing(self):
        """Test MissingMetadata when all fields are missing."""
        missing = MissingMetadata(
            album=True,
            year=True,
            album_artist=True,
            tracknumber=True,
            title=True
        )
        
        assert missing.album is True
        assert missing.year is True
        assert missing.album_artist is True
        assert missing.tracknumber is True
        assert missing.title is True


class TestFileProcessing:
    """Test suite for file processing methods."""
    
    @patch('album_metadata_editor.EasyID3')
    def test_update_mp3_metadata_basic(self, mock_easyid3):
        """Test basic MP3 metadata update."""
        editor = AlbumMetadataEditor(interactive=False)
        
        # Mock the audio object
        mock_audio = MagicMock()
        mock_easyid3.return_value = mock_audio
        
        metadata = AlbumMetadata(
            album_name="Test Album",
            year="2024",
            album_artist="Test Artist"
        )
        
        filepath = Path("/test/song.mp3")
        
        with patch('album_metadata_editor.ID3'):
            result = editor.update_mp3_metadata(filepath, metadata)
        
        assert result is True
        mock_audio.save.assert_called_once()
    
    @patch('album_metadata_editor.FLAC')
    def test_update_flac_metadata_basic(self, mock_flac):
        """Test basic FLAC metadata update."""
        editor = AlbumMetadataEditor(interactive=False)
        
        # Mock the audio object
        mock_audio = MagicMock()
        mock_audio.tags = {}
        mock_flac.return_value = mock_audio
        
        metadata = AlbumMetadata(
            album_name="Test Album",
            year="2024",
            album_artist="Test Artist"
        )
        
        filepath = Path("/test/song.flac")
        result = editor.update_flac_metadata(filepath, metadata)
        
        assert result is True
        mock_audio.save.assert_called_once()


# Integration tests would require actual audio files
@pytest.mark.integration
@pytest.mark.skip(reason="Requires actual audio test files")
class TestIntegration:
    """Integration tests requiring actual audio files."""
    
    def test_full_processing_workflow(self):
        """Test complete processing workflow with real files."""
        pass
    
    def test_metadata_preservation(self):
        """Test that metadata is correctly updated."""
        pass
    
    def test_file_renaming(self):
        """Test file renaming functionality."""
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])