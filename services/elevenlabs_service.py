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

    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess text to fix pronunciation issues and remove non-speech characters.

        Args:
            text: Original text

        Returns:
            Processed text with pronunciation fixes and clean speech
        """
        import re

        # Replace "911" with "nine one one" for correct pronunciation
        # Match "911" as a standalone word or at the beginning of a sentence
        processed = re.sub(r'\b911\b', 'nine one one', text)

        # Remove asterisks and other markdown formatting characters
        # Remove *text* (emphasis) and **text** (strong emphasis)
        processed = re.sub(r'\*+([^*]+)\*+', r'\1', processed)

        # Remove underscores used for emphasis _text_
        processed = re.sub(r'_+([^_]+)_+', r'\1', processed)

        # Remove tildes used for strikethrough ~~text~~
        processed = re.sub(r'~+([^~]+)~+', r'\1', processed)

        # Remove any remaining single asterisks, underscores, or tildes
        processed = re.sub(r'[*_~]', '', processed)

        # Remove extra whitespace that might result from removals
        processed = re.sub(r'\s+', ' ', processed).strip()

        return processed

    def text_to_speech(
        self,
        text: str,
        voice_id: str,
        stability: float = 0.5,
        clarity: float = 0.75,
        language: str = 'en'
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

            # Preprocess text to fix pronunciation issues
            processed_text = self._preprocess_text(text)

            # Select model based on language
            # Use multilingual model for non-English languages or mixed (translator) scenarios
            model_id = "eleven_multilingual_v2" if (language != 'en' or language == 'mixed') else "eleven_monolingual_v1"

            # For version 0.2.27, use simpler API call
            audio = generate(
                text=processed_text,
                voice=voice_id,
                model=model_id
            )

            return audio

        except Exception as e:
            self.logger.error(f"ElevenLabs API error: {str(e)}")
            raise Exception(f"Failed to generate speech: {str(e)}")

    def generate_dispatcher_audio(self, text: str, voice_id: str, language: str = 'en') -> bytes:
        """
        Generate audio for dispatcher with professional voice settings.

        Args:
            text: Dispatcher's text
            voice_id: Voice ID for dispatcher
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            Audio bytes
        """
        # Higher stability for professional, consistent tone
        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            stability=0.7,
            clarity=0.75,
            language=language
        )

    def generate_caller_audio(self, text: str, voice_id: str, emotion_level: str = 'concerned', language: str = 'en') -> bytes:
        """
        Generate audio for caller with emotional voice settings based on emotion level.

        Args:
            text: Caller's text
            voice_id: Voice ID for caller
            emotion_level: Emotion level (calm, concerned, anxious, panicked, hysterical)
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            Audio bytes
        """
        # Map emotion level to stability settings
        # Lower stability = more emotional variation
        stability_map = {
            'calm': 0.65,
            'concerned': 0.5,
            'anxious': 0.4,
            'panicked': 0.3,
            'hysterical': 0.2
        }
        stability = stability_map.get(emotion_level, 0.5)

        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            stability=stability,
            clarity=0.75,
            language=language
        )

    def generate_nurse_audio(self, text: str, voice_id: str, language: str = 'en') -> bytes:
        """
        Generate audio for nurse with calm, professional voice settings.

        Args:
            text: Nurse's text
            voice_id: Voice ID for nurse
            language: Language code (e.g., 'en', 'es', 'fr')

        Returns:
            Audio bytes
        """
        # Moderate stability for calm, professional, but conversational tone
        return self.text_to_speech(
            text=text,
            voice_id=voice_id,
            stability=0.6,
            clarity=0.75,
            language=language
        )

    def get_voice_info(self, voice_id: str) -> dict:
        """
        Get information about a specific voice by ID.

        Args:
            voice_id: ElevenLabs voice ID

        Returns:
            Dictionary with voice information including gender
        """
        try:
            all_voices = voices()
            for voice in all_voices:
                if voice.voice_id == voice_id:
                    labels = getattr(voice, 'labels', {})
                    gender = labels.get('gender', 'unknown') if isinstance(labels, dict) else 'unknown'
                    return {
                        'voice_id': voice.voice_id,
                        'name': voice.name,
                        'gender': gender,
                        'labels': labels
                    }
            # Voice not found, return unknown
            return {'voice_id': voice_id, 'name': 'Unknown', 'gender': 'unknown', 'labels': {}}
        except Exception as e:
            self.logger.error(f"Error getting voice info: {str(e)}")
            return {'voice_id': voice_id, 'name': 'Unknown', 'gender': 'unknown', 'labels': {}}

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
