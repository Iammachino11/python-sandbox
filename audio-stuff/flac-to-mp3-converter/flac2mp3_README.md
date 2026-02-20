# FLAC to MP3 Converter

A professional Python tool for converting FLAC audio files to MP3 format while preserving all metadata tags and album artwork.

## Features

- **High-Quality Conversion**: Converts FLAC to MP3 with configurable bitrate (default 320kbps)
- **Metadata Preservation**: Transfers all ID3 tags including artist, album, title, date, and more
- **Album Artwork**: Preserves embedded album art in the converted files
- **Batch Processing**: Convert entire directories of FLAC files at once
- **Progress Tracking**: Real-time conversion status and detailed statistics
- **Configurable Options**: Command-line arguments for customization
- **Error Handling**: Robust error handling with detailed logging
- **Duplicate Detection**: Skip already-converted files (optional overwrite)

## Installation

### Prerequisites

- Python 3.7 or higher
- FFmpeg (required by pydub)

#### Installing FFmpeg

**macOS:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Install Dependencies

```bash
pip install -r requirements.txt
```

Or install individually:
```bash
pip install mutagen pydub
```

## Usage

### Basic Usage

Convert all FLAC files in a directory:
```bash
python flac_to_mp3_converter.py /path/to/flac/files
```

Or run interactively (will prompt for directory):
```bash
python flac_to_mp3_converter.py
```

### Advanced Options

```bash
# Custom output directory
python flac_to_mp3_converter.py /path/to/flac -o /path/to/output

# Lower bitrate for smaller files
python flac_to_mp3_converter.py /path/to/flac -b 192k

# Overwrite existing files
python flac_to_mp3_converter.py /path/to/flac --overwrite

# Verbose logging
python flac_to_mp3_converter.py /path/to/flac --verbose

# Combine options
python flac_to_mp3_converter.py /path/to/flac -b 256k -o ~/Music/converted -v
```

### Command-Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `directory` | - | Directory containing FLAC files | Interactive prompt |
| `--output` | `-o` | Output directory | `<source>/converted` |
| `--bitrate` | `-b` | MP3 bitrate | `320k` |
| `--overwrite` | - | Overwrite existing files | `False` |
| `--verbose` | `-v` | Enable verbose logging | `False` |
| `--version` | - | Show version number | - |
| `--help` | `-h` | Show help message | - |

## Output

The converter creates an organized output with:
- All MP3 files in the `converted` folder (or custom output directory)
- Preserved file names (only extension changes)
- All metadata tags intact
- Embedded album artwork

### Example Output

```
INFO: Found 15 FLAC file(s)
INFO: Converting: 01 - Song Title.flac
INFO: Converted: 01 - Song Title.flac → 01 - Song Title.mp3
INFO: Converting: 02 - Another Song.flac
INFO: Converted: 02 - Another Song.flac → 02 - Another Song.mp3
...

==================================================
CONVERSION SUMMARY
==================================================
Total files:       15
Successfully converted: 14
Failed:            0
Skipped:           1
==================================================
```

## Supported Metadata Tags

The following tags are transferred from FLAC to MP3:
- Artist
- Album
- Title
- Date/Year
- Track Number
- Genre
- Comment
- Album Artist
- Composer
- Disc Number

## Error Handling

The tool includes comprehensive error handling for:
- Invalid directory paths
- Missing dependencies
- Corrupted audio files
- Metadata read/write errors
- Disk space issues
- Permission problems

Failed conversions are logged with detailed error messages while continuing with remaining files.

## Project Structure

```
flac-to-mp3-converter/
├── flac_to_mp3_converter.py  # Main script
├── requirements-dev.txt           # Python dependencies
├── requirements.txt           # Python dependencies
├── LICENSE                     # MIT License
├── flac2mp3_README.md                  # This file
└── tests.py                    # Unit tests (optional)
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

### Development Setup

1. Clone the repository
2. Install development dependencies: `pip install -r requirements-dev.txt`
3. Run tests: `pytest tests/`
4. Format code: `black flac_to_mp3_converter.py`
5. Lint code: `pylint flac_to_mp3_converter.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Mutagen](https://mutagen.readthedocs.io/) - Audio metadata handling
- [Pydub](https://pydub.com/) - Audio processing and conversion
- [FFmpeg](https://ffmpeg.org/) - Audio encoding backend

## Troubleshooting

### "No module named 'mutagen'" or similar
Install the required dependencies: `pip install -r requirements.txt`

### "FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'"
Install FFmpeg following the instructions in the Installation section.

### Permission denied errors
Ensure you have read permissions for source files and write permissions for the output directory.

### Album art not transferring
Some FLAC files may have non-standard picture formats. The converter will log a warning but still convert the audio.

## Roadmap

Future enhancements under consideration:
- [ ] GUI version
- [ ] Support for other formats (WAV, M4A, OGG)
- [ ] Parallel processing for faster batch conversion
- [ ] Automatic bitrate optimization based on source quality
- [ ] Web interface
- [ ] Docker container

## Author
[GitHub](https://github.com/Iammachino11)

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/Iammachino11/python-sandbox/audio-stuff/flac-to-mp3-converter/issues) on GitHub.