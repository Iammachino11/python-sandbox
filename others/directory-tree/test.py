"""
Unit tests for Directory Tree Generator

Run with: pytest tests/test_generator.py -v
"""

import pytest
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from directory_tree_generator import (
    DirectoryTreeGenerator,
    TreeConfig,
    TreeStats,
    OutputFormat
)


class TestTreeConfig:
    """Test suite for TreeConfig dataclass."""
    
    def test_config_initialization_defaults(self):
        """Test TreeConfig initialization with defaults."""
        config = TreeConfig()
        
        assert config.max_depth is None
        assert config.show_hidden is False
        assert config.dirs_only is False
        assert config.show_size is False
        assert config.show_permissions is False
        assert config.ignore_patterns == set()
    
    def test_config_initialization_custom(self):
        """Test TreeConfig initialization with custom values."""
        config = TreeConfig(
            max_depth=3,
            show_hidden=True,
            dirs_only=True,
            show_size=True,
            ignore_patterns={'node_modules', '*.pyc'}
        )
        
        assert config.max_depth == 3
        assert config.show_hidden is True
        assert config.dirs_only is True
        assert config.show_size is True
        assert config.ignore_patterns == {'node_modules', '*.pyc'}


class TestTreeStats:
    """Test suite for TreeStats dataclass."""
    
    def test_stats_initialization(self):
        """Test TreeStats initialization."""
        stats = TreeStats()
        
        assert stats.total_dirs == 0
        assert stats.total_files == 0
        assert stats.skipped == 0
        assert stats.errors == 0
    
    def test_stats_increment(self):
        """Test incrementing stats counters."""
        stats = TreeStats()
        
        stats.total_dirs = 10
        stats.total_files = 50
        stats.errors = 2
        
        assert stats.total_dirs == 10
        assert stats.total_files == 50
        assert stats.errors == 2


class TestOutputFormat:
    """Test suite for OutputFormat enum."""
    
    def test_output_format_values(self):
        """Test OutputFormat enum values."""
        assert OutputFormat.TEXT.value == "text"
        assert OutputFormat.MARKDOWN.value == "markdown"
        assert OutputFormat.HTML.value == "html"
        assert OutputFormat.JSON.value == "json"
    
    def test_output_format_enum(self):
        """Test OutputFormat enum construction."""
        format_text = OutputFormat("text")
        assert format_text == OutputFormat.TEXT


class TestDirectoryTreeGenerator:
    """Test suite for DirectoryTreeGenerator class."""
    
    def test_initialization_defaults(self):
        """Test generator initialization with defaults."""
        generator = DirectoryTreeGenerator()
        
        assert generator.config is not None
        assert generator.output_format == OutputFormat.TEXT
        assert isinstance(generator.stats, TreeStats)
        assert len(generator.ignore_patterns) > 0  # Has defaults
    
    def test_initialization_custom_config(self):
        """Test generator initialization with custom config."""
        config = TreeConfig(max_depth=3, show_hidden=True)
        generator = DirectoryTreeGenerator(
            config=config,
            output_format=OutputFormat.MARKDOWN
        )
        
        assert generator.config.max_depth == 3
        assert generator.config.show_hidden is True
        assert generator.output_format == OutputFormat.MARKDOWN
    
    def test_default_ignore_patterns(self):
        """Test that default ignore patterns are set."""
        generator = DirectoryTreeGenerator()
        
        assert '__pycache__' in generator.ignore_patterns
        assert '.git' in generator.ignore_patterns
        assert 'node_modules' in generator.ignore_patterns
        assert '.DS_Store' in generator.ignore_patterns
    
    def test_should_ignore_hidden_files(self):
        """Test ignoring hidden files."""
        config = TreeConfig(show_hidden=False)
        generator = DirectoryTreeGenerator(config=config)
        
        assert generator.should_ignore('.hidden_file') is True
        assert generator.should_ignore('normal_file') is False
    
    def test_should_ignore_show_hidden(self):
        """Test not ignoring hidden files when show_hidden is True."""
        config = TreeConfig(show_hidden=True)
        generator = DirectoryTreeGenerator(config=config)
        
        # Hidden files should not be ignored when show_hidden is True
        # unless they're in ignore_patterns
        assert generator.should_ignore('.random_hidden') is False
        assert generator.should_ignore('.git') is True  # In default ignore
    
    def test_should_ignore_patterns(self):
        """Test ignoring specific patterns."""
        config = TreeConfig(ignore_patterns={'test_*', 'temp'})
        generator = DirectoryTreeGenerator(config=config)
        
        assert generator.should_ignore('test_file.py') is True
        assert generator.should_ignore('temp') is True
        assert generator.should_ignore('normal.py') is False
    
    def test_should_ignore_wildcard(self):
        """Test wildcard pattern matching."""
        config = TreeConfig(ignore_patterns={'*.pyc', '*.log'})
        generator = DirectoryTreeGenerator(config=config)
        
        assert generator.should_ignore('file.pyc') is True
        assert generator.should_ignore('debug.log') is True
        assert generator.should_ignore('file.py') is False
    
    def test_format_size(self):
        """Test file size formatting."""
        generator = DirectoryTreeGenerator()
        
        assert generator._format_size(100) == "(100.0B)"
        assert generator._format_size(1024) == "(1.0KB)"
        assert generator._format_size(1024 * 1024) == "(1.0MB)"
        assert generator._format_size(1024 * 1024 * 1024) == "(1.0GB)"
    
    def test_get_entry_info_no_options(self):
        """Test get_entry_info with no display options."""
        config = TreeConfig(show_size=False, show_permissions=False)
        generator = DirectoryTreeGenerator(config=config)
        
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            info = generator.get_entry_info(path)
            assert info == ""
    
    def test_get_entry_info_with_size(self):
        """Test get_entry_info with size display."""
        config = TreeConfig(show_size=True)
        generator = DirectoryTreeGenerator(config=config)
        
        with tempfile.NamedTemporaryFile() as tmp:
            path = Path(tmp.name)
            path.write_bytes(b"test data")
            info = generator.get_entry_info(path)
            assert "B)" in info  # Should contain size


class TestTreeGeneration:
    """Test suite for tree generation methods."""
    
    def test_generate_tree_text_empty_dir(self):
        """Test generating tree for empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            generator = DirectoryTreeGenerator()
            lines = generator.generate_tree_text(Path(tmpdir))
            
            assert len(lines) == 0  # Empty directory
    
    def test_generate_tree_text_with_files(self):
        """Test generating tree with files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create test files
            Path(tmpdir, "file1.txt").touch()
            Path(tmpdir, "file2.txt").touch()
            
            generator = DirectoryTreeGenerator()
            lines = generator.generate_tree_text(Path(tmpdir))
            
            assert len(lines) == 2
            assert "file1.txt" in lines[0]
            assert "file2.txt" in lines[1]
    
    def test_generate_tree_text_with_subdirs(self):
        """Test generating tree with subdirectories."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create structure
            subdir = Path(tmpdir, "subdir")
            subdir.mkdir()
            Path(tmpdir, "file.txt").touch()
            Path(subdir, "subfile.txt").touch()
            
            generator = DirectoryTreeGenerator()
            lines = generator.generate_tree_text(Path(tmpdir))
            
            assert len(lines) > 2  # Parent and subdir files
            assert any("subdir" in line for line in lines)
            assert any("file.txt" in line for line in lines)
    
    def test_generate_tree_with_max_depth(self):
        """Test max depth limiting."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create nested structure
            level1 = Path(tmpdir, "level1")
            level2 = level1 / "level2"
            level3 = level2 / "level3"
            level3.mkdir(parents=True)
            
            config = TreeConfig(max_depth=1)
            generator = DirectoryTreeGenerator(config=config)
            lines = generator.generate_tree_text(Path(tmpdir))
            
            # Should only show level1, not deeper
            assert any("level1" in line for line in lines)
            # Level2 should not appear due to max_depth=1
            assert not any("level2" in line for line in lines)
    
    def test_generate_tree_dirs_only(self):
        """Test directories only mode."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file.txt").touch()
            Path(tmpdir, "subdir").mkdir()
            
            config = TreeConfig(dirs_only=True)
            generator = DirectoryTreeGenerator(config=config)
            lines = generator.generate_tree_text(Path(tmpdir))
            
            assert len(lines) == 1  # Only the subdir
            assert any("subdir" in line for line in lines)
            assert not any("file.txt" in line for line in lines)
    
    def test_generate_to_string_text(self):
        """Test generating tree as string."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.txt").touch()
            
            generator = DirectoryTreeGenerator()
            output = generator.generate_to_string(tmpdir)
            
            assert isinstance(output, str)
            assert "test.txt" in output
    
    def test_generate_to_file_text(self):
        """Test generating tree to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "test.txt").touch()
            output_file = Path(tmpdir, "tree.txt")
            
            generator = DirectoryTreeGenerator()
            stats = generator.generate_to_file(tmpdir, str(output_file))
            
            assert output_file.exists()
            assert stats.total_files >= 1
            
            content = output_file.read_text()
            assert "test.txt" in content
    
    def test_invalid_directory(self):
        """Test error handling for invalid directory."""
        generator = DirectoryTreeGenerator()
        
        with pytest.raises(FileNotFoundError):
            generator.generate_to_string("/nonexistent/directory")


class TestMarkdownGeneration:
    """Test suite for Markdown generation."""
    
    def test_generate_markdown(self):
        """Test Markdown format generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file.txt").touch()
            
            generator = DirectoryTreeGenerator(output_format=OutputFormat.MARKDOWN)
            lines = generator.generate_tree_markdown(Path(tmpdir))
            
            assert len(lines) > 0
            assert any("file.txt" in line for line in lines)
            assert any("-" in line for line in lines)  # Markdown list


class TestHTMLGeneration:
    """Test suite for HTML generation."""
    
    def test_generate_html(self):
        """Test HTML format generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file.txt").touch()
            
            generator = DirectoryTreeGenerator(output_format=OutputFormat.HTML)
            lines = generator.generate_tree_html(Path(tmpdir))
            
            assert len(lines) > 0
            assert any("<html>" in line for line in lines)
            assert any("</html>" in line for line in lines)
            assert any("file.txt" in line for line in lines)


class TestJSONGeneration:
    """Test suite for JSON generation."""
    
    def test_generate_json(self):
        """Test JSON format generation."""
        with tempfile.TemporaryDirectory() as tmpdir:
            Path(tmpdir, "file.txt").touch()
            
            generator = DirectoryTreeGenerator(output_format=OutputFormat.JSON)
            tree = generator.generate_tree_json(Path(tmpdir))
            
            assert isinstance(tree, dict)
            assert "name" in tree
            assert "type" in tree
            assert "children" in tree
            assert tree["type"] == "directory"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])