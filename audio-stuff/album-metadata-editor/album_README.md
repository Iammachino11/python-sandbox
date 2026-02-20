# Album Metadata Editor

A professional Python tool for batch updating album metadata, artwork, and file naming for MP3 and FLAC audio files.

## Features

- **Multi-Format Support**: Works with both MP3 and FLAC files
- **Batch Metadata Updates**: Update album, year, and artist for entire directories
- **Album Artwork**: Embed cover art from image files
- **Smart File Renaming**: Rename files based on track number and title
- **Missing Metadata Detection**: Automatically identifies incomplete tags
- **Interactive & Non-Interactive Modes**: Use interactively or in scripts
- **Progress Tracking**: Detailed statistics and logging
- **Configurable Options**: Command-line arguments for automation
- **Error Handling**: Robust error handling with graceful failures

## Installation

### Prerequisites

- Python 3.7 or higher
- mutagen library for audio metadata handling

### Install Dependencies

```bash
pip install mutagen
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

Update all audio files in a directory:
```bash
python album_metadata_editor.py /path/to/album
```

The script will:
1. Find all MP3/FLAC files
2. Look for cover.jpg (or similar) in the directory
3. Prompt for any missing metadata
4. Update all files with the metadata and artwork

### Interactive Mode (Default)

```bash
# Script will prompt for missing information
python album_metadata_editor.py /path/to/album
```

Example interaction:
```
Enter album name: Dark Side of the Moon
Enter album year: 1973
Enter album artist: Pink Floyd
Do you want to rename files? (y/n): y
```

### Advanced Options

```bash
# Rename files automatically
python album_metadata_editor.py /path/to/album --rename

# Use custom cover art
python album_metadata_editor.py /path/to/album --cover /path/to/artwork.jpg

# Provide metadata via command line (non-interactive)
python album_metadata_editor.py /path/to/album \
    --album "Album Name" \
    --year "2024" \
    --artist "Artist Name" \
    --non-interactive

# Rename and use verbose logging
python album_metadata_editor.py /path/to/album --rename --verbose

# Complete automation example
python album_metadata_editor.py /path/to/album \
    --album "Greatest Hits" \
    --year "2024" \
    --artist "The Band" \
    --cover cover.jpg \
    --rename \
    --non-interactive
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `directory` | - | Directory containing audio files | Interactive prompt |
| `--cover` | `-c` | Path to cover art file | Looks for cover.jpg/cover.png/folder.jpg |
| `--rename` | `-r` | Rename files based on metadata | `False` |
| `--album` | - | Album name (skips prompt) | Interactive prompt |
| `--year` | - | Album year (skips prompt) | Interactive prompt |
| `--artist` | - | Album artist (skips prompt) | Interactive prompt |
| `--non-interactive` | - | No prompts (for scripts) | `False` |
| `--auto-number` | - | Auto-generate track numbers | `False` |
| `--verbose` | `-v` | Enable verbose logging | `False` |
| `--version` | - | Show version number | - |
| `--help` | `-h` | Show help message | - |

## File Naming

When using the `--rename` option, files are renamed using this format:
```
01 - Song Title.mp3
02 - Another Song.flac
03 - Yet Another Track.mp3
```

Features:
- Track numbers are zero-padded (01, 02, etc.)
- Handles track numbers in "2/10" format
- Removes invalid filename characters
- Preserves original file extension

## Cover Art

The script automatically searches for cover art in the following order:
1. `cover.jpg`
2. `cover.png`
3. `folder.jpg`
4. `album.jpg`

Or specify a custom path:
```bash
python album_metadata_editor.py /path/to/album --cover artwork.png
```

## Supported Metadata Tags

The tool updates the following tags:
- **Album Name**: Album title
- **Year/Date**: Release year
- **Album Artist**: Primary album artist
- **Track Number**: Track number (for renaming)
- **Title**: Track title (for renaming)
- **Cover Art**: Embedded album artwork

## Output Examples

### Standard Update
```
INFO: Found 12 audio file(s)
INFO: Found cover art: cover.jpg
Enter album name: Abbey Road
Enter album year: 1969
Enter album artist: The Beatles

INFO: Updated: 01.mp3
INFO: Updated: 02.mp3
...

==================================================
PROCESSING SUMMARY
==================================================
Total files:       12
Updated:           12
Failed:            0
Skipped:           0
==================================================
```

### With Renaming
```
INFO: Found 12 audio file(s)
INFO: Found cover art: cover.jpg
Enter album name: Abbey Road
Enter album year: 1969
Enter album artist: The Beatles

Rename files based on metadata? (y/n): y

INFO: Updated and renamed: 01.mp3 → 01 - Come Together.mp3
INFO: Updated and renamed: 02.mp3 → 02 - Something.mp3
...

==================================================
PROCESSING SUMMARY
==================================================
Total files:       12
Updated:           12
Renamed:           12
Failed:            0
Skipped:           0
==================================================
```

## Use Cases

### 1. New Album Organization
Just downloaded an album? Organize it properly:
```bash
python album_metadata_editor.py ~/Downloads/NewAlbum --rename
```

### 2. Fix Missing Metadata
Album has files but no proper tags:
```bash
python album_metadata_editor.py /path/to/album \
    --album "Correct Album Name" \
    --year "2024" \
    --artist "Correct Artist"
```

### 3. Update Artwork Only
Files have correct metadata but missing artwork:
```bash
python album_metadata_editor.py /path/to/album \
    --cover new_artwork.jpg \
    --non-interactive
```

### 4. Batch Processing Script
Process multiple albums automatically:
```bash
for dir in /music/*/; do
    python album_metadata_editor.py "$dir" --non-interactive --verbose
done
```

### 5. Standardize File Names
Rename all files in a consistent format:
```bash
python album_metadata_editor.py /path/to/album --rename --non-interactive
```

## Error Handling

The tool handles various error conditions gracefully:
- **Missing files**: Continues with available files
- **Corrupted metadata**: Logs warning and continues
- **Invalid cover art**: Proceeds without artwork
- **Permission errors**: Reports error for specific file
- **Missing metadata**: Prompts user or skips if non-interactive

Failed files are logged and counted in the summary.

## Project Structure

```
album-metadata-editor/
├── album_metadata_editor.py   # Main script
├── album_README.md             # This file
├── LICENSE                     # MIT License
├── requirements.txt            # Python dependencies
├── test.py                      # Unit tests

```

## Scripting Examples

### Bash Script for Batch Processing
```bash
#!/bin/bash
# Process all album directories

MUSIC_DIR="/path/to/music"

for album_dir in "$MUSIC_DIR"/*; do
    if [ -d "$album_dir" ]; then
        echo "Processing: $album_dir"
        python album_metadata_editor.py "$album_dir" --non-interactive --verbose
    fi
done
```

### Python Script for Custom Processing
```python
from album_metadata_editor import AlbumMetadataEditor, AlbumMetadata

# Create editor
editor = AlbumMetadataEditor(rename_files=True, interactive=False)

# Process directory with custom metadata
metadata = AlbumMetadata(
    album_name="Custom Album",
    year="2024",
    album_artist="Artist Name"
)

# Process
stats = editor.process_directory("/path/to/album")
print(f"Updated {stats.updated} files")
```

## Troubleshooting

### "No supported audio files found"
- Ensure the directory contains .mp3 or .flac files
- Check file extensions (case-insensitive matching is supported)

### "No cover art found"
- Add a file named `cover.jpg`, `cover.png`, `folder.jpg`, or `album.jpg`
- Or specify custom path with `--cover`

### "Error reading metadata"
- File may be corrupted or not a valid audio file
- Try with `--verbose` to see detailed error messages

### Files not renaming
- Ensure track number and title metadata exist
- Use interactive mode to manually enter missing information
- Files without complete metadata will skip renaming

### Permission errors
- Ensure you have write permissions for the directory
- Check that files aren't in use by other programs

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `pytest tests/`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Mutagen](https://mutagen.readthedocs.io/) - Audio metadata handling library

## Roadmap

Future enhancements:
- [ ] Support for additional audio formats (M4A, OGG, WAV)
- [ ] Automatic metadata fetching from online databases
- [ ] GUI version
- [ ] Playlist generation
- [ ] Duplicate detection
- [ ] Automatic artwork downloading
- [ ] Bulk editing interface

## Author
[GitHub](https://github.com/Iammachino11)


## Support

If you encounter any issues, please [open an issue](https://github.com/Iammachino11/python-sandbox/audio-stuff/album-metadata-editor/issues) on GitHub.