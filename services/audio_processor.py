"""Audio processing service for combining and manipulating audio segments."""

from pydub import AudioSegment
from pydub.generators import WhiteNoise, Sine, Square
from io import BytesIO
import logging
import random
import os


class AudioProcessor:
    """Processes and combines audio segments into complete conversations."""

    def __init__(self):
        """Initialize AudioProcessor."""
        self.logger = logging.getLogger(__name__)

        # Audio quality settings (bitrate in kbps, sample rate in Hz)
        self.quality_settings = {
            'high': {'bitrate': '192k', 'sample_rate': 44100},
            'medium': {'bitrate': '128k', 'sample_rate': 32000},
            'low': {'bitrate': '64k', 'sample_rate': 22050},
            'very_low': {'bitrate': '32k', 'sample_rate': 16000}
        }

        # Background noise volume adjustments (in dB)
        self.noise_levels = {
            'none': None,
            'light': -30,
            'moderate': -20,
            'heavy': -10,
            'extreme': -5
        }

        # Ambient samples directory
        self.ambient_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            'static', 'audio', 'ambient'
        )

        # Map noise types to sample filenames
        self.sample_files = {
            'static': 'phone-static.mp3',
            'dispatch': 'dispatch-center.mp3',
            'traffic': 'traffic-road.mp3',
            'sirens': 'emergency-sirens.mp3',
            'crowd': 'crowd-murmur.mp3',
            'wind': 'wind-outdoor.mp3'
        }

    def combine_dialogue_audio(
        self,
        dialogue: list,
        audio_segments: list,
        audio_quality: str = 'high',
        background_noise_type: str = 'none',
        background_noise_level: str = 'moderate'
    ) -> AudioSegment:
        """
        Combine audio segments into a single conversation.

        Args:
            dialogue: List of dialogue items with pause_after field
            audio_segments: List of audio bytes from TTS
            audio_quality: Quality level (high, medium, low, very_low)
            background_noise_type: Type of noise (none, static, dispatch, traffic, sirens, crowd, wind)
            background_noise_level: Volume level (light, moderate, heavy, extreme)

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

        # Apply quality settings
        combined = self.apply_quality_settings(combined, audio_quality)

        # Add background noise
        combined = self.add_background_noise(combined, background_noise_type, background_noise_level)

        return combined

    def create_diarized_audio(
        self,
        dialogue: list,
        audio_segments: list,
        audio_quality: str = 'high',
        background_noise_type: str = 'none',
        background_noise_level: str = 'moderate'
    ) -> AudioSegment:
        """
        Create stereo audio with speakers on separate channels.
        Dispatcher on left channel, caller on right channel.

        Args:
            dialogue: List of dialogue items with speaker and pause_after
            audio_segments: List of audio bytes from TTS
            audio_quality: Quality level (high, medium, low, very_low)
            background_noise_type: Type of noise (none, static, dispatch, traffic, sirens, crowd, wind)
            background_noise_level: Volume level (light, moderate, heavy, extreme)

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
            else:  # caller or nurse
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

        # Apply quality settings
        stereo = self.apply_quality_settings(stereo, audio_quality)

        # Add background noise
        stereo = self.add_background_noise(stereo, background_noise_type, background_noise_level)

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

    def apply_quality_settings(
        self,
        audio: AudioSegment,
        quality: str = 'high'
    ) -> AudioSegment:
        """
        Apply quality degradation to simulate different connection types.

        Args:
            audio: Input AudioSegment
            quality: Quality level (high, medium, low, very_low)

        Returns:
            AudioSegment with applied quality settings
        """
        if quality not in self.quality_settings:
            self.logger.warning(f"Unknown quality '{quality}', using 'high'")
            quality = 'high'

        settings = self.quality_settings[quality]
        sample_rate = settings['sample_rate']

        self.logger.info(f"Applying quality settings: {quality} ({sample_rate} Hz)")

        # Change sample rate (this degrades quality by resampling)
        audio = audio.set_frame_rate(sample_rate)

        return audio

    def load_ambient_sample(self, noise_type: str, duration_ms: int) -> AudioSegment:
        """
        Load ambient audio sample from file and loop to match duration.

        Args:
            noise_type: Type of noise (static, dispatch, traffic, etc.)
            duration_ms: Target duration in milliseconds

        Returns:
            AudioSegment of ambient noise, or None if file not found
        """
        if noise_type not in self.sample_files:
            return None

        sample_filename = self.sample_files[noise_type]
        sample_path = os.path.join(self.ambient_dir, sample_filename)

        if not os.path.exists(sample_path):
            self.logger.warning(f"Ambient sample not found: {sample_path}, falling back to tone synthesis")
            return None

        try:
            # Load the sample
            sample = AudioSegment.from_file(sample_path)
            self.logger.info(f"Loaded ambient sample: {sample_filename} ({len(sample)}ms)")

            # If sample is shorter than needed duration, loop it
            if len(sample) < duration_ms:
                loops_needed = (duration_ms // len(sample)) + 1
                looped = sample * loops_needed
                # Trim to exact duration
                result = looped[:duration_ms]
                self.logger.debug(f"Looped sample {loops_needed} times to reach {duration_ms}ms")
            else:
                # Sample is long enough, just trim it
                result = sample[:duration_ms]

            return result

        except Exception as e:
            self.logger.error(f"Error loading ambient sample {sample_path}: {e}")
            return None

    def generate_background_noise(self, duration_ms: int, noise_type: str = 'static') -> AudioSegment:
        """
        Generate background noise - first tries to load from sample file, falls back to tone synthesis.

        Args:
            duration_ms: Duration in milliseconds
            noise_type: Type of noise (static, dispatch, traffic, sirens, crowd, wind)

        Returns:
            AudioSegment with generated noise
        """
        self.logger.info(f"Generating {noise_type} noise: {duration_ms}ms")

        # First try to load from sample file
        sample = self.load_ambient_sample(noise_type, duration_ms)
        if sample is not None:
            return sample

        # Fall back to tone synthesis if sample not available
        self.logger.info(f"Using tone synthesis for {noise_type} noise")

        if noise_type == 'static':
            # Phone static - white noise filtered
            noise = WhiteNoise().to_audio_segment(duration=duration_ms)
            noise = noise.set_frame_rate(8000).set_frame_rate(44100)
            noise = noise - 5

        elif noise_type == 'dispatch':
            # Dispatch center - office hum + muffled voices
            # 60Hz electrical hum
            hum = Sine(60).to_audio_segment(duration=duration_ms) - 25

            # Add harmonics for richness
            hum2 = Sine(120).to_audio_segment(duration=duration_ms) - 30

            # Filtered white noise for office ambiance
            ambient = WhiteNoise().to_audio_segment(duration=duration_ms)
            ambient = ambient.set_frame_rate(8000).set_frame_rate(44100) - 20

            # Mix all layers
            noise = hum.overlay(hum2).overlay(ambient)

        elif noise_type == 'traffic':
            # Traffic - engine rumble using low frequency tones
            # Multiple engine tones at different frequencies
            engine1 = Sine(40).to_audio_segment(duration=duration_ms) - 15
            engine2 = Sine(55).to_audio_segment(duration=duration_ms) - 18
            engine3 = Sine(80).to_audio_segment(duration=duration_ms) - 20

            # Road noise (filtered white noise)
            road = WhiteNoise().to_audio_segment(duration=duration_ms)
            road = road.set_frame_rate(3000).set_frame_rate(44100) - 18

            # Mix engines and road
            noise = engine1.overlay(engine2).overlay(engine3).overlay(road)

        elif noise_type == 'sirens':
            # Emergency sirens - oscillating tones
            base_silence = AudioSegment.silent(duration=duration_ms)

            # Create segments with varying siren tones
            segment_length = 800  # ms per segment
            position = 0

            while position < duration_ms:
                # Alternate between two siren frequencies (distant effect)
                if (position // segment_length) % 2 == 0:
                    freq = 650 + random.randint(-50, 50)
                else:
                    freq = 750 + random.randint(-50, 50)

                seg_duration = min(segment_length, duration_ms - position)
                tone = Sine(freq).to_audio_segment(duration=seg_duration) - 25
                base_silence = base_silence.overlay(tone, position=position)
                position += segment_length

            # Add ambient noise
            ambient = WhiteNoise().to_audio_segment(duration=duration_ms)
            ambient = ambient.set_frame_rate(10000).set_frame_rate(44100) - 25

            noise = base_silence.overlay(ambient)

        elif noise_type == 'crowd':
            # Crowd - multiple voice-like frequencies
            # Human speech ranges from 85-255 Hz (fundamental frequencies)
            voice1 = Sine(110).to_audio_segment(duration=duration_ms) - 22
            voice2 = Sine(150).to_audio_segment(duration=duration_ms) - 24
            voice3 = Sine(200).to_audio_segment(duration=duration_ms) - 23
            voice4 = Sine(130).to_audio_segment(duration=duration_ms) - 25

            # Add formants (higher frequencies that make it sound like voices)
            formant1 = Sine(800).to_audio_segment(duration=duration_ms) - 28
            formant2 = Sine(1200).to_audio_segment(duration=duration_ms) - 30

            # White noise for consonants/breath
            chatter = WhiteNoise().to_audio_segment(duration=duration_ms)
            chatter = chatter.set_frame_rate(12000).set_frame_rate(44100) - 25

            # Mix all voice-like components
            noise = voice1.overlay(voice2).overlay(voice3).overlay(voice4)
            noise = noise.overlay(formant1).overlay(formant2).overlay(chatter)

        elif noise_type == 'wind':
            # Wind - low frequency rumble with variation
            # Very low frequencies for wind
            wind1 = Sine(30).to_audio_segment(duration=duration_ms) - 18
            wind2 = Sine(45).to_audio_segment(duration=duration_ms) - 20
            wind3 = Sine(65).to_audio_segment(duration=duration_ms) - 22

            # Filtered noise for texture
            texture = WhiteNoise().to_audio_segment(duration=duration_ms)
            texture = texture.set_frame_rate(2000).set_frame_rate(44100) - 22

            noise = wind1.overlay(wind2).overlay(wind3).overlay(texture)

        else:
            # Default to static
            noise = WhiteNoise().to_audio_segment(duration=duration_ms)
            noise = noise.set_frame_rate(8000).set_frame_rate(44100)

        return noise

    def add_background_noise(
        self,
        audio: AudioSegment,
        noise_type: str = 'none',
        noise_level: str = 'moderate'
    ) -> AudioSegment:
        """
        Add background noise to audio at specified type and level.

        Args:
            audio: Input AudioSegment (dialogue)
            noise_type: Type of noise (none, static, dispatch, traffic, sirens, crowd, wind)
            noise_level: Volume level (light, moderate, heavy, extreme)

        Returns:
            AudioSegment with background noise mixed in
        """
        # If no noise type, return original
        if noise_type == 'none':
            self.logger.info("No background noise requested")
            return audio

        if noise_level not in self.noise_levels:
            self.logger.warning(f"Unknown noise level '{noise_level}', using 'moderate'")
            noise_level = 'moderate'

        noise_db = self.noise_levels[noise_level]
        if noise_db is None:
            noise_db = -20  # Default moderate level

        self.logger.info(f"Adding background noise: {noise_type} at {noise_level} level ({noise_db} dB)")

        # Generate noise matching the audio duration and type
        noise = self.generate_background_noise(len(audio), noise_type)

        # Adjust noise volume (negative dB = quieter)
        noise = noise + noise_db

        # Overlay the noise with the dialogue
        # The dialogue should be on top (more prominent)
        result = noise.overlay(audio)

        self.logger.info("Background noise mixed successfully")
        return result
