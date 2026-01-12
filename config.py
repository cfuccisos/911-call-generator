import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Application configuration class."""

    # Flask settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

    # API Keys
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    ELEVENLABS_API_KEY = os.getenv('ELEVENLABS_API_KEY')

    # ElevenLabs Voice IDs (optional - can be selected in UI)
    DISPATCHER_VOICE_ID = os.getenv('DISPATCHER_VOICE_ID')
    CALLER_VOICE_ID = os.getenv('CALLER_VOICE_ID')

    # Audio Settings
    AUDIO_OUTPUT_DIR = os.path.join('static', 'audio')
    MAX_PROMPT_LENGTH = 500
    ALLOWED_AUDIO_FORMATS = ['mp3', 'wav']

    # File cleanup settings
    AUDIO_FILE_LIFETIME = 3600  # 1 hour in seconds

    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        # Only API keys are required - voice IDs are now selectable in UI
        required_keys = [
            ('GEMINI_API_KEY', cls.GEMINI_API_KEY),
            ('ELEVENLABS_API_KEY', cls.ELEVENLABS_API_KEY),
        ]

        missing = [key for key, value in required_keys if not value]

        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file."
            )
