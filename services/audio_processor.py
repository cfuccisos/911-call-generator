"""Audio processing service for combining and manipulating audio segments."""

from pydub import AudioSegment
from io import BytesIO
import logging


class AudioProcessor:
    """Processes and combines audio segments into complete conversations."""

    def __init__(self):
        """Initialize AudioProcessor."""
        self.logger = logging.getLogger(__name__)

    def combine_dialogue_audio(
        self,
        dialogue: list,
        audio_segments: list
    ) -> AudioSegment:
        """
        Combine audio segments into a single conversation.

        Args:
            dialogue: List of dialogue items with pause_after field
            audio_segments: List of audio bytes from TTS

        Returns:
            Combined AudioSegment

        Raises:
            ValueError: If dialogue and audio_segments lengths don't match
        """
        if len(dialogue) != len(audio_segments):
            raise ValueError(
                f"Dialogue length ({len(dialogue)}) doesn't match "
                f"audio segments length ({len(audio_segments)})"
            )

        self.logger.info("Combining audio segments...")
        combined = AudioSegment.empty()

        for i, item in enumerate(dialogue):
            # Convert bytes to AudioSegment
            audio = AudioSegment.from_mp3(BytesIO(audio_segments[i]))

            # Add audio segment to combined track
            combined += audio

            # Add pause/silence after this segment
            pause_ms = int(item['pause_after'] * 1000)
            silence = AudioSegment.silent(duration=pause_ms)
            combined += silence

            self.logger.debug(
                f"Added segment {i+1}/{len(dialogue)}: "
                f"{item['speaker']} ({len(audio)}ms + {pause_ms}ms pause)"
            )

        self.logger.info(
            f"Combined audio created: {len(combined)}ms "
            f"({len(combined)/1000:.1f} seconds)"
        )
        return combined

    def create_diarized_audio(
        self,
        dialogue: list,
        audio_segments: list
    ) -> AudioSegment:
        """
        Create stereo audio with speakers on separate channels.
        Dispatcher on left channel, caller on right channel.

        Args:
            dialogue: List of dialogue items with speaker and pause_after
            audio_segments: List of audio bytes from TTS

        Returns:
            Stereo AudioSegment with diarized speakers

        Raises:
            ValueError: If dialogue and audio_segments lengths don't match
        """
        if len(dialogue) != len(audio_segments):
            raise ValueError(
                f"Dialogue length ({len(dialogue)}) doesn't match "
                f"audio segments length ({len(audio_segments)})"
            )

        self.logger.info("Creating diarized stereo audio...")

        # Calculate total duration needed
        total_duration = 0
        for i, item in enumerate(dialogue):
            audio = AudioSegment.from_mp3(BytesIO(audio_segments[i]))
            total_duration += len(audio) + int(item['pause_after'] * 1000)

        self.logger.info(f"Total duration: {total_duration}ms ({total_duration/1000:.1f}s)")

        # Create silent mono channels for left (dispatcher) and right (caller)
        left_channel = AudioSegment.silent(duration=total_duration)
        right_channel = AudioSegment.silent(duration=total_duration)

        # Overlay audio segments on appropriate channel
        position = 0
        for i, item in enumerate(dialogue):
            audio = AudioSegment.from_mp3(BytesIO(audio_segments[i]))

            if item['speaker'] == 'dispatcher':
                left_channel = left_channel.overlay(audio, position=position)
                channel_name = "left"
            else:  # caller
                right_channel = right_channel.overlay(audio, position=position)
                channel_name = "right"

            self.logger.debug(
                f"Overlaid segment {i+1} ({item['speaker']}) on {channel_name} "
                f"channel at {position}ms"
            )

            # Move position forward
            position += len(audio) + int(item['pause_after'] * 1000)

        # Combine mono channels into stereo
        stereo = AudioSegment.from_mono_audiosegments(left_channel, right_channel)

        self.logger.info(
            f"Diarized stereo audio created: {len(stereo)}ms, "
            f"channels={stereo.channels}"
        )

        return stereo

    def convert_to_audiosegment(self, audio_bytes: bytes) -> AudioSegment:
        """
        Convert audio bytes to AudioSegment.

        Args:
            audio_bytes: Raw audio bytes (typically MP3)

        Returns:
            AudioSegment object
        """
        return AudioSegment.from_mp3(BytesIO(audio_bytes))
