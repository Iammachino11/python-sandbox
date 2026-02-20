#!/usr/bin/env python3
"""
FLAC to MP3 Converter
A professional audio conversion tool that converts FLAC files to MP3 format
while preserving metadata and album artwork.

Author: MACHINO11
License:
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Tuple
from dataclasses import dataclass

try:
    from mutagen.flac import FLAC
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    from mutagen import MutagenError
    from pydub import AudioSegment
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Install dependencies with: pip install mutagen pydub")
    sys.exit(1)


@dataclass
class ConversionStats:
    """Statistics for the conversion process."""
    total_files: int = 0
    successful: int = 0
    failed: int = 0
    skipped: int = 0


class FlacToMp3Converter:
    """Converts FLAC audio files to MP3 format with metadata preservation."""

    # Tag mapping between FLAC and MP3 (ID3v2)
    TAG_MAP = {
        'artist': 'ARTIST',
        'album': 'ALBUM',
        'title': 'TITLE',
        'date': 'DATE',
        'tracknumber': 'TRACKNUMBER',
        'genre': 'GENRE',
        'comment': 'COMMENT',
        'albumartist': 'ALBUMARTIST',
        'composer': 'COMPOSER',
        'discnumber': 'DISCNUMBER',
    }

    def __init__(
            self,
            output_dir: Optional[str] = None,
            bitrate: str = "320k",
            overwrite: bool = False,
            verbose: bool = False
    ):
        """
        Initialize the converter.

        Args:
            output_dir: Custom output directory (default: 'converted' subfolder)
            bitrate: MP3 bitrate (default: 320k)
            overwrite: Whether to overwrite existing files
            verbose: Enable verbose logging
        """
        self.output_dir = output_dir
        self.bitrate = bitrate
        self.overwrite = overwrite
        self.stats = ConversionStats()

        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def find_flac_files(self, directory: str) -> List[Path]:
        """
        Find all FLAC files in the specified directory.

        Args:
            directory: Directory path to search

        Returns:
            List of Path objects for FLAC files
        """
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        flac_files = set()
        for pattern in ("*.flac", "*.FLAC"):
            flac_files.update(path.glob(pattern))

        flac_files = list(flac_files)
        self.logger.info(f"Found {len(flac_files)} FLAC file(s)")
        return flac_files

    def create_output_directory(self, source_dir: str) -> Path:
        """
        Create the output directory for converted files.

        Args:
            source_dir: Source directory containing FLAC files

        Returns:
            Path object for the output directory
        """
        if self.output_dir:
            output_path = Path(self.output_dir)
        else:
            output_path = Path(source_dir) / "converted"

        output_path.mkdir(parents=True, exist_ok=True)
        self.logger.debug(f"Output directory: {output_path}")
        return output_path

    def convert_audio(self, flac_path: Path, mp3_path: Path) -> bool:
        """
        Convert FLAC audio to MP3 format.

        Args:
            flac_path: Source FLAC file path
            mp3_path: Destination MP3 file path

        Returns:
            True if successful, False otherwise
        """
        try:
            audio = AudioSegment.from_file(str(flac_path), format="flac")
            audio.export(
                str(mp3_path),
                format="mp3",
                bitrate=self.bitrate,
                parameters=["-q:a", "0"]  # Highest quality VBR
            )
            return True
        except Exception as e:
            self.logger.error(f"Audio conversion failed: {e}")
            return False

    def transfer_metadata(self, flac_path: Path, mp3_path: Path) -> bool:
        """
        Transfer metadata tags from FLAC to MP3.

        Args:
            flac_path: Source FLAC file path
            mp3_path: Destination MP3 file path

        Returns:
            True if successful, False otherwise
        """
        try:
            flac = FLAC(str(flac_path))

            # Initialize MP3 tags
            try:
                mp3_tags = EasyID3(str(mp3_path))
            except MutagenError:
                mp3_tags = EasyID3()
                mp3_tags.save(str(mp3_path))
                mp3_tags = EasyID3(str(mp3_path))

            # Transfer standard tags
            tags_transferred = 0
            for id3_tag, flac_tag in self.TAG_MAP.items():
                if flac_tag in flac.tags:
                    values = flac.tags[flac_tag]
                    if values:
                        mp3_tags[id3_tag] = str(values[0])
                        tags_transferred += 1

            mp3_tags.save()
            self.logger.debug(f"Transferred {tags_transferred} metadata tag(s)")
            return True

        except Exception as e:
            self.logger.error(f"Metadata transfer failed: {e}")
            return False

    def transfer_album_art(self, flac_path: Path, mp3_path: Path) -> bool:
        """
        Transfer album artwork from FLAC to MP3.

        Args:
            flac_path: Source FLAC file path
            mp3_path: Destination MP3 file path

        Returns:
            True if successful, False otherwise
        """
        try:
            flac = FLAC(str(flac_path))

            if not flac.pictures:
                self.logger.debug("No album art found in FLAC file")
                return True

            id3 = ID3(str(mp3_path))
            id3.delall('APIC')  # Remove existing covers

            picture = flac.pictures[0]
            id3.add(APIC(
                encoding=3,  # UTF-8
                mime=picture.mime,
                type=picture.type,
                desc=picture.desc or 'Cover',
                data=picture.data
            ))
            id3.save(v2_version=3)

            self.logger.debug("Album art transferred successfully")
            return True

        except Exception as e:
            self.logger.error(f"Album art transfer failed: {e}")
            return False

    def convert_file(
            self,
            flac_path: Path,
            output_dir: Path
    ) -> Tuple[bool, str]:
        """
        Convert a single FLAC file to MP3.

        Args:
            flac_path: Path to the FLAC file
            output_dir: Output directory for the MP3 file

        Returns:
            Tuple of (success: bool, message: str)
        """
        mp3_filename = flac_path.stem + ".mp3"
        mp3_path = output_dir / mp3_filename

        # Check if file already exists
        if mp3_path.exists() and not self.overwrite:
            self.stats.skipped += 1
            return False, f"Skipped (already exists): {flac_path.name}"

        self.logger.info(f"Converting: {flac_path.name}")

        # Convert audio
        if not self.convert_audio(flac_path, mp3_path):
            self.stats.failed += 1
            return False, f"Failed (audio conversion): {flac_path.name}"

        # Transfer metadata
        if not self.transfer_metadata(flac_path, mp3_path):
            self.logger.warning("Metadata transfer failed, but file converted")

        # Transfer album art
        if not self.transfer_album_art(flac_path, mp3_path):
            self.logger.warning("Album art transfer failed, but file converted")

        self.stats.successful += 1
        return True, f"Converted: {flac_path.name} → {mp3_filename}"

    def convert_directory(self, directory: str) -> ConversionStats:
        """
        Convert all FLAC files in a directory to MP3.

        Args:
            directory: Directory containing FLAC files

        Returns:
            ConversionStats object with conversion statistics
        """
        try:
            # Find FLAC files
            flac_files = self.find_flac_files(directory)

            if not flac_files:
                self.logger.warning("No FLAC files found in the directory")
                return self.stats

            # Create output directory
            output_dir = self.create_output_directory(directory)

            # Convert files
            self.stats.total_files = len(flac_files)

            for flac_path in flac_files:
                try:
                    success, message = self.convert_file(flac_path, output_dir)
                    if success or self.stats.skipped > 0:
                        self.logger.info(message)
                    else:
                        self.logger.error(message)

                except Exception as e:
                    self.stats.failed += 1
                    self.logger.error(f"Error processing {flac_path.name}: {e}")

            # Print summary
            self._print_summary()
            return self.stats

        except (FileNotFoundError, NotADirectoryError) as e:
            self.logger.error(str(e))
            return self.stats

    def _print_summary(self):
        """Print conversion summary statistics."""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("CONVERSION SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total files:       {self.stats.total_files}")
        self.logger.info(f"Successfully converted: {self.stats.successful}")
        self.logger.info(f"Failed:            {self.stats.failed}")
        self.logger.info(f"Skipped:           {self.stats.skipped}")
        self.logger.info("=" * 50)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Convert FLAC audio files to MP3 format with metadata preservation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/flac/files
  %(prog)s /path/to/flac/files -b 192k
  %(prog)s /path/to/flac/files -o /path/to/output
  %(prog)s /path/to/flac/files --overwrite --verbose
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        help='Directory containing FLAC files (prompts if not provided)'
    )

    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: <source>/converted)'
    )

    parser.add_argument(
        '-b', '--bitrate',
        default='320k',
        help='MP3 bitrate (default: 320k)'
    )

    parser.add_argument(
        '--overwrite',
        action='store_true',
        help='Overwrite existing MP3 files'
    )

    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )

    parser.add_argument(
        '--version',
        action='version',
        version='%(prog)s 1.0.0'
    )

    args = parser.parse_args()

    # Get directory from argument or prompt user
    directory = args.directory
    if not directory:
        directory = input("Enter the directory containing FLAC files: ").strip()

    if not directory:
        print("Error: No directory specified")
        sys.exit(1)

    # Create converter and run
    converter = FlacToMp3Converter(
        output_dir=args.output,
        bitrate=args.bitrate,
        overwrite=args.overwrite,
        verbose=args.verbose
    )

    try:
        stats = converter.convert_directory(directory)

        # Exit with appropriate code
        if stats.failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nConversion cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()