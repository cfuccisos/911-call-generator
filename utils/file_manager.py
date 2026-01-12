"""File management utilities for the 911 Call Generator."""

import os
import time
import uuid
from datetime import datetime
from pydub import AudioSegment


class FileManager:
    """Manages audio file storage and cleanup."""

    def __init__(self, output_dir: str):
        """
        Initialize FileManager.

        Args:
            output_dir: Directory path for storing audio files
        """
        self.output_dir = output_dir
        self._ensure_directory_exists()

    def _ensure_directory_exists(self):
        """Create output directory if it doesn't exist."""
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_unique_filename(self, audio_format: str) -> str:
        """
        Generate a unique filename for audio files.

        Args:
            audio_format: File extension (mp3, wav)

        Returns:
            Unique filename with timestamp and UUID
        """
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = str(uuid.uuid4())[:8]
        return f"call_{timestamp}_{unique_id}.{audio_format}"

    def save_audio_file(self, audio: AudioSegment, filename: str, audio_format: str) -> str:
        """
        Save audio file to disk.

        Args:
            audio: AudioSegment object
            filename: Name of the file
            audio_format: Format (mp3 or wav)

        Returns:
            Full filepath of saved file
        """
        filepath = os.path.join(self.output_dir, filename)

        if audio_format == 'mp3':
            audio.export(
                filepath,
                format='mp3',
                bitrate='192k',
                parameters=['-ar', '44100']
            )
        elif audio_format == 'wav':
            audio.export(
                filepath,
                format='wav',
                parameters=['-ar', '44100', '-sample_fmt', 's16']
            )
        else:
            raise ValueError(f"Unsupported audio format: {audio_format}")

        return filepath

    def get_file_path(self, filename: str) -> str:
        """
        Get full path for a filename.

        Args:
            filename: Name of the file

        Returns:
            Full filepath

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        filepath = os.path.join(self.output_dir, filename)

        # Security: Prevent directory traversal
        if not os.path.abspath(filepath).startswith(os.path.abspath(self.output_dir)):
            raise ValueError("Invalid filename")

        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filename}")

        return filepath

    def cleanup_old_files(self, max_age_seconds: int):
        """
        Delete files older than specified age.

        Args:
            max_age_seconds: Maximum age of files in seconds
        """
        if not os.path.exists(self.output_dir):
            return

        current_time = time.time()
        deleted_count = 0

        for filename in os.listdir(self.output_dir):
            # Skip .gitkeep
            if filename == '.gitkeep':
                continue

            filepath = os.path.join(self.output_dir, filename)

            # Skip if not a file
            if not os.path.isfile(filepath):
                continue

            # Check file age
            file_age = current_time - os.path.getmtime(filepath)

            if file_age > max_age_seconds:
                try:
                    os.remove(filepath)
                    deleted_count += 1
                except Exception as e:
                    print(f"Error deleting {filepath}: {e}")

        if deleted_count > 0:
            print(f"Cleaned up {deleted_count} old audio file(s)")
