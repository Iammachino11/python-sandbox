"""
Unit tests for FLAC to MP3 Converter

Run with: pytest tests/test_converter.py -v
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Assuming the main script is importable
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flac_to_mp3_converter import FlacToMp3Converter, ConversionStats


class TestFlacToMp3Converter:
    """Test suite for FlacToMp3Converter class."""
    
    def test_initialization_default_params(self):
        """Test converter initialization with default parameters."""
        converter = FlacToMp3Converter()
        
        assert converter.output_dir is None
        assert converter.bitrate == "320k"
        assert converter.overwrite is False
        assert isinstance(converter.stats, ConversionStats)
    
    def test_initialization_custom_params(self):
        """Test converter initialization with custom parameters."""
        converter = FlacToMp3Converter(
            output_dir="/custom/path",
            bitrate="192k",
            overwrite=True,
            verbose=True
        )
        
        assert converter.output_dir == "/custom/path"
        assert converter.bitrate == "192k"
        assert converter.overwrite is True
    
    def test_find_flac_files_empty_directory(self):
        """Test finding FLAC files in an empty directory."""
        converter = FlacToMp3Converter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            flac_files = converter.find_flac_files(tmpdir)
            assert len(flac_files) == 0
    
    def test_find_flac_files_invalid_directory(self):
        """Test finding FLAC files with invalid directory."""
        converter = FlacToMp3Converter()
        
        with pytest.raises(FileNotFoundError):
            converter.find_flac_files("/nonexistent/directory")
    
    def test_create_output_directory(self):
        """Test output directory creation."""
        converter = FlacToMp3Converter()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = converter.create_output_directory(tmpdir)
            
            assert output_dir.exists()
            assert output_dir.is_dir()
            assert output_dir.name == "converted"
    
    def test_create_custom_output_directory(self):
        """Test custom output directory creation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            custom_output = os.path.join(tmpdir, "custom_output")
            converter = FlacToMp3Converter(output_dir=custom_output)
            
            output_dir = converter.create_output_directory(tmpdir)
            
            assert output_dir.exists()
            assert str(output_dir) == custom_output
    
    def test_conversion_stats_initialization(self):
        """Test ConversionStats dataclass initialization."""
        stats = ConversionStats()
        
        assert stats.total_files == 0
        assert stats.successful == 0
        assert stats.failed == 0
        assert stats.skipped == 0
    
    @patch('flac_to_mp3_converter.AudioSegment.from_file')
    def test_convert_audio_success(self, mock_from_file):
        """Test successful audio conversion."""
        converter = FlacToMp3Converter()
        
        # Mock AudioSegment
        mock_audio = MagicMock()
        mock_from_file.return_value = mock_audio
        
        with tempfile.TemporaryDirectory() as tmpdir:
            flac_path = Path(tmpdir) / "test.flac"
            mp3_path = Path(tmpdir) / "test.mp3"
            
            # Create dummy FLAC file
            flac_path.touch()
            
            result = converter.convert_audio(flac_path, mp3_path)
            
            assert result is True
            mock_from_file.assert_called_once()
            mock_audio.export.assert_called_once()
    
    def test_tag_map_completeness(self):
        """Test that TAG_MAP contains expected tags."""
        expected_tags = [
            'artist', 'album', 'title', 'date', 
            'tracknumber', 'genre', 'comment'
        ]
        
        for tag in expected_tags:
            assert tag in FlacToMp3Converter.TAG_MAP


class TestConversionStats:
    """Test suite for ConversionStats dataclass."""
    
    def test_stats_increment(self):
        """Test incrementing stats counters."""
        stats = ConversionStats()
        
        stats.total_files = 10
        stats.successful = 8
        stats.failed = 1
        stats.skipped = 1
        
        assert stats.total_files == 10
        assert stats.successful == 8
        assert stats.failed == 1
        assert stats.skipped == 1


# Integration tests would require actual FLAC files
# These are examples of what you might test:

@pytest.mark.integration
@pytest.mark.skip(reason="Requires actual FLAC test files")
class TestIntegration:
    """Integration tests requiring actual audio files."""
    
    def test_full_conversion_workflow(self):
        """Test complete conversion workflow with real files."""
        # This would test the entire process with actual FLAC files
        pass
    
    def test_metadata_preservation(self):
        """Test that all metadata is correctly preserved."""
        # This would verify metadata transfer with real files
        pass
    
    def test_album_art_transfer(self):
        """Test album artwork is correctly transferred."""
        # This would verify album art with real files
        pass


if __name__ == "__main__":
    pytest.main([__file__, "-v"])