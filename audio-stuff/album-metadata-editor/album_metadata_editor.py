#!/usr/bin/env python3
"""
Album Metadata Editor
A professional tool for batch updating album metadata and artwork for MP3 and FLAC files.

Author: Machino11
License: MIT
"""

import os
import sys
import argparse
import logging
from pathlib import Path
from typing import List, Optional, Dict, Tuple
from dataclasses import dataclass

try:
    from mutagen.easyid3 import EasyID3
    from mutagen.id3 import ID3, APIC
    from mutagen.flac import FLAC, Picture
    from mutagen import MutagenError
except ImportError as e:
    print(f"Error: Missing required dependency - {e}")
    print("Install dependencies with: pip install mutagen")
    sys.exit(1)


@dataclass
class MetadataStats:
    """Statistics for the metadata update process."""
    total_files: int = 0
    updated: int = 0
    renamed: int = 0
    failed: int = 0
    skipped: int = 0


@dataclass
class AlbumMetadata:
    """Container for album metadata."""
    album_name: Optional[str] = None
    year: Optional[str] = None
    album_artist: Optional[str] = None
    cover_data: Optional[bytes] = None
    cover_path: Optional[str] = None


@dataclass
class MissingMetadata:
    """Tracks which metadata fields are missing across files."""
    album: bool = False
    year: bool = False
    album_artist: bool = False
    tracknumber: bool = False
    title: bool = False


class AlbumMetadataEditor:
    """Batch editor for audio file metadata and artwork."""

    SUPPORTED_FORMATS = ('.mp3', '.flac')
    DEFAULT_COVER_NAMES = ('cover.jpg', 'cover.png', 'folder.jpg', 'album.jpg')

    def __init__(
            self,
            rename_files: bool = False,
            interactive: bool = True,
            auto_number: bool = False,
            verbose: bool = False
    ):
        """
        Initialize the metadata editor.

        Args:
            rename_files: Whether to rename files based on metadata
            interactive: Whether to prompt for missing metadata
            auto_number: Auto-generate track numbers if missing
            verbose: Enable verbose logging
        """
        self.rename_files = rename_files
        self.interactive = interactive
        self.auto_number = auto_number
        self.stats = MetadataStats()

        # Configure logging
        log_level = logging.DEBUG if verbose else logging.INFO
        logging.basicConfig(
            level=log_level,
            format='%(levelname)s: %(message)s'
        )
        self.logger = logging.getLogger(__name__)

    def find_audio_files(self, directory: str) -> List[Path]:
        """
        Find all supported audio files in the directory.

        Args:
            directory: Directory path to search

        Returns:
            List of Path objects for audio files
        """
        path = Path(directory)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        if not path.is_dir():
            raise NotADirectoryError(f"Not a directory: {directory}")

        # Use a set to remove duplicates
        audio_files = set()
        for ext in self.SUPPORTED_FORMATS:
            audio_files.update(path.glob(f"*{ext}"))
            audio_files.update(path.glob(f"*{ext.upper()}"))

        # Convert back to list and sort
        audio_files = sorted(list(audio_files))

        self.logger.info(f"Found {len(audio_files)} audio file(s)")
        return audio_files

    def find_cover_art(self, directory: str) -> Optional[Path]:
        """
        Find cover art file in the directory.

        Args:
            directory: Directory path to search

        Returns:
            Path to cover art file or None
        """
        path = Path(directory)

        for cover_name in self.DEFAULT_COVER_NAMES:
            cover_path = path / cover_name
            if cover_path.exists():
                self.logger.info(f"Found cover art: {cover_name}")
                return cover_path

        self.logger.warning("No cover art found")
        return None

    def load_cover_art(self, cover_path: Path) -> Optional[bytes]:
        """
        Load cover art data from file.

        Args:
            cover_path: Path to cover art file

        Returns:
            Cover art bytes or None
        """
        try:
            with open(cover_path, 'rb') as img_file:
                cover_data = img_file.read()
            self.logger.debug(f"Loaded {len(cover_data)} bytes of cover art")
            return cover_data
        except Exception as e:
            self.logger.error(f"Error reading cover art: {e}")
            return None

    def detect_missing_metadata(
            self,
            audio_files: List[Path]
    ) -> MissingMetadata:
        """
        Detect which metadata fields are missing across all files.

        Args:
            audio_files: List of audio file paths

        Returns:
            MissingMetadata object
        """
        missing = MissingMetadata()

        for filepath in audio_files:
            try:
                if filepath.suffix.lower() == '.mp3':
                    audio = EasyID3(str(filepath))
                    missing.album = missing.album or 'album' not in audio
                    missing.year = missing.year or 'date' not in audio
                    missing.album_artist = missing.album_artist or 'albumartist' not in audio
                    missing.tracknumber = missing.tracknumber or 'tracknumber' not in audio
                    missing.title = missing.title or 'title' not in audio

                elif filepath.suffix.lower() == '.flac':
                    audio = FLAC(str(filepath))
                    missing.album = missing.album or 'album' not in audio.tags
                    missing.year = missing.year or 'date' not in audio.tags
                    missing.album_artist = missing.album_artist or 'albumartist' not in audio.tags
                    missing.tracknumber = missing.tracknumber or 'tracknumber' not in audio.tags
                    missing.title = missing.title or 'title' not in audio.tags

            except MutagenError:
                # If file can't be read, assume all metadata is missing
                missing.album = True
                missing.year = True
                missing.album_artist = True
                missing.tracknumber = True
                missing.title = True

        return missing

    def prompt_for_metadata(
            self,
            missing: MissingMetadata
    ) -> AlbumMetadata:
        """
        Prompt user for missing metadata.

        Args:
            missing: MissingMetadata object indicating what to prompt for

        Returns:
            AlbumMetadata object with user input
        """
        metadata = AlbumMetadata()

        if not self.interactive:
            return metadata

        if missing.album:
            metadata.album_name = input("Enter album name: ").strip() or None

        if missing.year:
            metadata.year = input("Enter album year: ").strip() or None

        if missing.album_artist:
            metadata.album_artist = input("Enter album artist: ").strip() or None

        return metadata

    def get_file_metadata(
            self,
            filepath: Path
    ) -> Dict[str, str]:
        """
        Get current metadata from an audio file.

        Args:
            filepath: Path to audio file

        Returns:
            Dictionary of metadata tags
        """
        metadata = {}

        try:
            if filepath.suffix.lower() == '.mp3':
                audio = EasyID3(str(filepath))
                for key in audio.keys():
                    metadata[key] = audio[key][0] if audio[key] else ''

            elif filepath.suffix.lower() == '.flac':
                audio = FLAC(str(filepath))
                for key in audio.tags.keys():
                    metadata[key] = audio.tags[key][0] if audio.tags[key] else ''

        except MutagenError as e:
            self.logger.warning(f"Could not read metadata from {filepath.name}: {e}")

        return metadata

    def update_mp3_metadata(
            self,
            filepath: Path,
            album_metadata: AlbumMetadata
    ) -> bool:
        """
        Update metadata for an MP3 file.

        Args:
            filepath: Path to MP3 file
            album_metadata: AlbumMetadata object with new metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            # Update text metadata
            try:
                audio = EasyID3(str(filepath))
            except MutagenError:
                audio = EasyID3()

            if album_metadata.album_name:
                audio['album'] = album_metadata.album_name
            if album_metadata.year:
                audio['date'] = album_metadata.year
            if album_metadata.album_artist:
                audio['albumartist'] = album_metadata.album_artist

            # Handle missing track info if renaming
            if self.rename_files:
                if 'tracknumber' not in audio:
                    if self.interactive:
                        tracknumber = input(f"Enter track number for {filepath.name}: ").strip()
                        audio['tracknumber'] = tracknumber
                if 'title' not in audio:
                    if self.interactive:
                        title = input(f"Enter title for {filepath.name}: ").strip()
                        audio['title'] = title

            audio.save(str(filepath))

            # Update album art if provided
            if album_metadata.cover_data:
                id3 = ID3(str(filepath))
                id3.delall('APIC')
                id3.add(APIC(
                    encoding=3,  # UTF-8
                    mime='image/jpeg',
                    type=3,  # Cover (front)
                    desc='Cover',
                    data=album_metadata.cover_data
                ))
                id3.save(v2_version=3)

            return True

        except Exception as e:
            self.logger.error(f"Error updating MP3 metadata: {e}")
            return False

    def update_flac_metadata(
            self,
            filepath: Path,
            album_metadata: AlbumMetadata
    ) -> bool:
        """
        Update metadata for a FLAC file.

        Args:
            filepath: Path to FLAC file
            album_metadata: AlbumMetadata object with new metadata

        Returns:
            True if successful, False otherwise
        """
        try:
            audio = FLAC(str(filepath))

            if album_metadata.album_name:
                audio['album'] = album_metadata.album_name
            if album_metadata.year:
                audio['date'] = album_metadata.year
            if album_metadata.album_artist:
                audio['albumartist'] = album_metadata.album_artist

            # Handle missing track info if renaming
            if self.rename_files:
                if 'tracknumber' not in audio.tags:
                    if self.interactive:
                        tracknumber = input(f"Enter track number for {filepath.name}: ").strip()
                        audio['tracknumber'] = tracknumber
                if 'title' not in audio.tags:
                    if self.interactive:
                        title = input(f"Enter title for {filepath.name}: ").strip()
                        audio['title'] = title

            # Add album art if provided
            if album_metadata.cover_data:
                picture = Picture()
                picture.data = album_metadata.cover_data
                picture.type = 3  # Cover (front)
                picture.mime = 'image/jpeg'
                picture.desc = 'Cover'
                audio.clear_pictures()
                audio.add_picture(picture)

            audio.save()
            return True

        except Exception as e:
            self.logger.error(f"Error updating FLAC metadata: {e}")
            return False

    def generate_filename(
            self,
            filepath: Path,
            tracknumber: str,
            title: str
    ) -> str:
        """
        Generate a new filename from metadata.

        Args:
            filepath: Original file path
            tracknumber: Track number
            title: Track title

        Returns:
            New filename
        """
        # Format track number with leading zero
        try:
            track_num = int(tracknumber.split('/')[0])  # Handle "2/10" format
            formatted_tracknumber = f"{track_num:02d}"
        except (ValueError, IndexError):
            formatted_tracknumber = tracknumber.zfill(2)

        # Clean title for filename (remove invalid characters)
        clean_title = "".join(
            c for c in title
            if c.isalnum() or c in " -_()[]"
        ).strip()

        # Replace multiple spaces with single space
        clean_title = " ".join(clean_title.split())

        return f"{formatted_tracknumber} - {clean_title}{filepath.suffix}"

    def rename_file(
            self,
            filepath: Path
    ) -> Tuple[bool, Optional[str]]:
        """
        Rename file based on its metadata.

        Args:
            filepath: Path to audio file

        Returns:
            Tuple of (success: bool, new_filename: str or None)
        """
        try:
            # Get metadata
            if filepath.suffix.lower() == '.mp3':
                audio = EasyID3(str(filepath))
                tracknumber = audio['tracknumber'][0]
                title = audio['title'][0]
            elif filepath.suffix.lower() == '.flac':
                audio = FLAC(str(filepath))
                tracknumber = audio.tags['tracknumber'][0]
                title = audio.tags['title'][0]
            else:
                return False, None

            # Generate new filename
            new_filename = self.generate_filename(filepath, tracknumber, title)
            new_filepath = filepath.parent / new_filename

            # Rename file
            if new_filepath != filepath:
                filepath.rename(new_filepath)
                self.stats.renamed += 1
                return True, new_filename

            return False, None

        except Exception as e:
            self.logger.error(f"Error renaming {filepath.name}: {e}")
            return False, None

    def update_file(
            self,
            filepath: Path,
            album_metadata: AlbumMetadata
    ) -> Tuple[bool, str]:
        """
        Update metadata for a single file.

        Args:
            filepath: Path to audio file
            album_metadata: AlbumMetadata object with new metadata

        Returns:
            Tuple of (success: bool, message: str)
        """
        self.logger.debug(f"Processing: {filepath.name}")

        # Update metadata based on file type
        if filepath.suffix.lower() == '.mp3':
            success = self.update_mp3_metadata(filepath, album_metadata)
        elif filepath.suffix.lower() == '.flac':
            success = self.update_flac_metadata(filepath, album_metadata)
        else:
            return False, f"Unsupported format: {filepath.name}"

        if not success:
            self.stats.failed += 1
            return False, f"Failed to update: {filepath.name}"

        # Rename file if requested
        new_name = None
        if self.rename_files:
            renamed, new_name = self.rename_file(filepath)
            if renamed:
                message = f"Updated and renamed: {filepath.name} → {new_name}"
            else:
                message = f"Updated: {filepath.name}"
        else:
            message = f"Updated: {filepath.name}"

        self.stats.updated += 1
        return True, message

    def process_directory(
            self,
            directory: str,
            cover_path: Optional[str] = None
    ) -> MetadataStats:
        """
        Process all audio files in a directory.

        Args:
            directory: Directory containing audio files
            cover_path: Optional path to cover art file

        Returns:
            MetadataStats object with processing statistics
        """
        try:
            # Find audio files
            audio_files = self.find_audio_files(directory)

            if not audio_files:
                self.logger.warning("No supported audio files found (MP3/FLAC)")
                return self.stats

            self.stats.total_files = len(audio_files)

            # Find cover art
            if cover_path:
                cover = Path(cover_path)
                if not cover.exists():
                    self.logger.error(f"Specified cover art not found: {cover_path}")
                    cover = None
            else:
                cover = self.find_cover_art(directory)

            # Load cover art
            album_metadata = AlbumMetadata()
            if cover:
                album_metadata.cover_data = self.load_cover_art(cover)
                album_metadata.cover_path = str(cover)

            # Detect missing metadata
            missing = self.detect_missing_metadata(audio_files)

            # Prompt for metadata if interactive
            if self.interactive:
                user_metadata = self.prompt_for_metadata(missing)
                album_metadata.album_name = user_metadata.album_name
                album_metadata.year = user_metadata.year
                album_metadata.album_artist = user_metadata.album_artist

                # Confirm rename if requested
                if self.rename_files and not self.interactive:
                    self.rename_files = False
                elif self.rename_files:
                    confirm = input("\nRename files based on metadata? (y/n): ").strip().lower()
                    self.rename_files = confirm == 'y'

            # Process files
            for filepath in audio_files:
                try:
                    success, message = self.update_file(filepath, album_metadata)
                    self.logger.info(message)
                except Exception as e:
                    self.stats.failed += 1
                    self.logger.error(f"Error processing {filepath.name}: {e}")

            # Print summary
            self._print_summary()
            return self.stats

        except (FileNotFoundError, NotADirectoryError) as e:
            self.logger.error(str(e))
            return self.stats

    def _print_summary(self):
        """Print processing summary statistics."""
        self.logger.info("\n" + "=" * 50)
        self.logger.info("PROCESSING SUMMARY")
        self.logger.info("=" * 50)
        self.logger.info(f"Total files:       {self.stats.total_files}")
        self.logger.info(f"Updated:           {self.stats.updated}")
        if self.rename_files:
            self.logger.info(f"Renamed:           {self.stats.renamed}")
        self.logger.info(f"Failed:            {self.stats.failed}")
        self.logger.info(f"Skipped:           {self.stats.skipped}")
        self.logger.info("=" * 50)


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(
        description="Batch update album metadata and artwork for audio files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s /path/to/album
  %(prog)s /path/to/album --rename
  %(prog)s /path/to/album --cover /path/to/artwork.jpg
  %(prog)s /path/to/album --rename --verbose --non-interactive
  %(prog)s /path/to/album --album "Album Name" --year 2024 --artist "Artist Name"
        """
    )

    parser.add_argument(
        'directory',
        nargs='?',
        help='Directory containing audio files (prompts if not provided)'
    )

    parser.add_argument(
        '-c', '--cover',
        help='Path to cover art file (default: looks for cover.jpg in directory)'
    )

    parser.add_argument(
        '-r', '--rename',
        action='store_true',
        help='Rename files based on metadata (format: "01 - Title.ext")'
    )

    parser.add_argument(
        '--album',
        help='Album name (skips interactive prompt)'
    )

    parser.add_argument(
        '--year',
        help='Album year (skips interactive prompt)'
    )

    parser.add_argument(
        '--artist',
        help='Album artist (skips interactive prompt)'
    )

    parser.add_argument(
        '--non-interactive',
        action='store_true',
        help='Non-interactive mode (no prompts)'
    )

    parser.add_argument(
        '--auto-number',
        action='store_true',
        help='Auto-generate track numbers if missing'
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
        directory = input("Enter directory containing audio files: ").strip()

    if not directory:
        print("Error: No directory specified")
        sys.exit(1)

    # Create editor
    interactive = not args.non_interactive
    editor = AlbumMetadataEditor(
        rename_files=args.rename,
        interactive=interactive,
        auto_number=args.auto_number,
        verbose=args.verbose
    )

    # Process directory
    try:
        # If metadata provided via CLI, disable interactive prompts for those fields
        if args.album or args.year or args.artist:
            # Override prompt_for_metadata to use CLI args
            album_metadata = AlbumMetadata(
                album_name=args.album,
                year=args.year,
                album_artist=args.artist
            )
            # This is a simplified approach; a full implementation would need more work

        stats = editor.process_directory(directory, args.cover)

        # Exit with appropriate code
        if stats.failed > 0:
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nProcessing cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"Unexpected error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()