"""ElevenLabs service for text-to-speech conversion."""

from elevenlabs import generate, set_api_key, voices
import logging
import requests


class ElevenLabsService:
    """Service for generating speech audio using ElevenLabs TTS."""

    def __init__(self, api_key: str):
        """
        Initialize ElevenLabsService.

        Args:
            api_key: ElevenLabs API key
        """
        set_api_key(api_key)
        self.api_key = api_key
        self.logger = logging.getLogger(__name__)

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        stability: float = 0.5,
        clarity: float = 0.75
    ) -> bytes:
        """
        Convert text to speech using ElevenLabs.

        Args:
            text: Text to convert to speech
            voice_id: ElevenLabs voice ID
            stability: Voice consistency (0-1, higher = more consistent)
            clarity: Voice similarity boost (0-1, higher = more similar to original)

        Returns:
            Audio data as bytes

        Raises:
            Exception: If TTS generation fails
        """
        try:
            self.logger.info(f"Generating speech for: {text[:50]}...")

            # For version 0.2.27, use simpler API call
            audio = generate(
                text=text,
                voice=voice_id,
                model="eleven_monolingual_v1"
            )

            return audio

        except Exception as e:
            self.logger.error(f"ElevenLabs API error: {str(e)}")
            raise Exception(f"Failed to generate speech: {str(e)}")

    def generate_dispatcher_audio(self, text: str, voice_id: str) -> bytes:
        """
        Generate audio for dispatcher with professional voice settings.

        Args:
            text: Dispatcher's text
            voice_id: Voice ID for dispatcher

        Returns:
            Audio bytes
        """
        # Higher stability for professional, consistent tone
        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            stability=0.7,
            clarity=0.75
        )

    def generate_caller_audio(self, text: str, voice_id: str) -> bytes:
        """
        Generate audio for caller with more emotional voice settings.

        Args:
            text: Caller's text
            voice_id: Voice ID for caller

        Returns:
            Audio bytes
        """
        # Lower stability for more emotional, varied tone
        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            stability=0.5,
            clarity=0.75
        )

    def get_available_voices(self) -> list:
        """
        Fetch list of available voices from ElevenLabs.

        Returns:
            List of voice dictionaries with id, name, and preview_url
        """
        try:
            self.logger.info("Fetching available voices from ElevenLabs...")

            # Use the elevenlabs SDK to get voices
            all_voices = voices()

            # Format response for frontend
            voice_list = []
            for voice in all_voices:
                voice_data = {
                    'voice_id': voice.voice_id,
                    'name': voice.name,
                    'category': getattr(voice, 'category', 'unknown'),
                    'description': getattr(voice, 'description', ''),
                    'labels': getattr(voice, 'labels', {}),
                    'preview_url': getattr(voice, 'preview_url', None)
                }
                voice_list.append(voice_data)

            self.logger.info(f"Retrieved {len(voice_list)} voices")
            return voice_list

        except Exception as e:
            self.logger.error(f"Error fetching voices: {str(e)}")
            # Return a fallback list with some common voices
            return self._get_fallback_voices()

    def _get_fallback_voices(self) -> list:
        """
        Return a fallback list of common ElevenLabs voices.

        Returns:
            List of default voice dictionaries
        """
        return [
            {
                'voice_id': '21m00Tcm4TlvDq8ikWAM',
                'name': 'Rachel (Professional Female)',
                'category': 'premade',
                'description': 'Clear, professional female voice',
                'labels': {},
                'preview_url': None
            },
            {
                'voice_id': 'ErXwobaYiN019PkySvjV',
                'name': 'Antoni (Calm Male)',
                'category': 'premade',
                'description': 'Well-rounded, calm male voice',
                'labels': {},
                'preview_url': None
            },
            {
                'voice_id': 'VR6AewLTigWG4xSOukaG',
                'name': 'Arnold (Authoritative Male)',
                'category': 'premade',
                'description': 'Crisp, authoritative male voice',
                'labels': {},
                'preview_url': None
            },
            {
                'voice_id': 'pNInz6obpgDQGcFmaJgB',
                'name': 'Adam (Deep Male)',
                'category': 'premade',
                'description': 'Deep, resonant male voice',
                'labels': {},
                'preview_url': None
            },
            {
                'voice_id': 'EXAVITQu4vr4xnSDxMaL',
                'name': 'Bella (Expressive Female)',
                'category': 'premade',
                'description': 'Expressive, emotional female voice',
                'labels': {},
                'preview_url': None
            }
        ]

    def generate_preview(self, voice_id: str, sample_text: str = None) -> bytes:
        """
        Generate a preview audio sample for a voice.

        Args:
            voice_id: ElevenLabs voice ID
            sample_text: Optional custom text for preview

        Returns:
            Audio bytes for preview
        """
        if sample_text is None:
            sample_text = "Hello, this is a voice preview. How can I assist you today?"

        try:
            return self.text_to_speech(
                text=sample_text,
                voice_id=voice_id,
                stability=0.5,
                clarity=0.75
            )
        except Exception as e:
            self.logger.error(f"Error generating preview: {str(e)}")
            raise
