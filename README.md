# 911 Call Generator

A Flask web application that generates realistic 911 emergency call audio from text prompts. The application uses Google Gemini for dialogue generation and ElevenLabs for high-quality text-to-speech conversion.

## Purpose

This tool is designed for testing and training purposes, allowing developers and trainers to generate realistic 911 call audio without needing actual emergency recordings.

## Features

- **AI-Generated Dialogue**: Uses Google Gemini to create realistic conversations between a 911 dispatcher and caller
- **High-Quality Voice Synthesis**: Leverages ElevenLabs TTS for natural-sounding audio
- **Dual Speaker Support**: Separate voices for dispatcher and caller
- **Multiple Audio Formats**: Export as MP3 or WAV
- **Diarization Option**: Create stereo audio with speakers on separate channels (dispatcher on left, caller on right)
- **Web Interface**: User-friendly browser-based interface
- **Auto-Cleanup**: Automatically removes old audio files to save disk space

## Requirements

### System Requirements

- Python 3.8 or higher
- ffmpeg (required for audio processing)

### API Keys Required

1. **Google Gemini API Key**
   - Get it from [Google AI Studio](https://makersuite.google.com/app/apikey)

2. **ElevenLabs API Key**
   - Sign up at [ElevenLabs](https://elevenlabs.io/)
   - Get your API key from the dashboard

3. **ElevenLabs Voice IDs**
   - Browse voices at [ElevenLabs Voice Library](https://elevenlabs.io/app/voice-library)
   - You'll need two voice IDs: one for dispatcher, one for caller
   - Recommended: Choose a professional, calm voice for dispatcher and a more varied voice for caller

## Installation

### 1. Install System Dependencies

**macOS** (using Homebrew):
```bash
brew install ffmpeg
```

**Ubuntu/Debian**:
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows**:
Download ffmpeg from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### 2. Clone or Download the Project

```bash
cd ~/Desktop
# The project is already in ~/Desktop/911-call-generator/
cd 911-call-generator
```

### 3. Create Virtual Environment

```bash
python3 -m venv venv
```

### 4. Activate Virtual Environment

**macOS/Linux**:
```bash
source venv/bin/activate
```

**Windows**:
```bash
venv\Scripts\activate
```

### 5. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 6. Configure Environment Variables

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your API keys:
   ```bash
   nano .env  # or use your preferred text editor
   ```

3. Fill in the required values:
   ```env
   SECRET_KEY=your-secret-key-here
   GEMINI_API_KEY=your-google-gemini-api-key
   ELEVENLABS_API_KEY=your-elevenlabs-api-key
   DISPATCHER_VOICE_ID=your-dispatcher-voice-id
   CALLER_VOICE_ID=your-caller-voice-id
   ```

## Usage

### Starting the Application

1. Make sure your virtual environment is activated
2. Run the Flask application:
   ```bash
   python app.py
   ```

3. Open your browser and navigate to:
   ```
   http://localhost:5000
   ```

### Generating a Call

1. **Enter a Scenario**: Describe the emergency situation in the text area
   - Example: "Car accident on Highway 101 with multiple injuries"
   - Keep it under 500 characters

2. **Select Audio Format**:
   - **MP3**: Compressed format, smaller file size
   - **WAV**: Uncompressed format, higher quality

3. **Enable Diarization** (optional):
   - Check this box to create stereo audio with speakers on separate channels
   - Useful for analysis or processing tools that need speaker separation
   - Dispatcher on left channel, caller on right channel

4. **Click "Generate Call"**: The process takes 10-30 seconds depending on dialogue length

5. **Play and Download**: Once generated, you can play the audio in the browser or download it

### Example Scenarios

Here are some example prompts you can try:

- "Medical emergency: elderly person fell and can't get up, possible hip fracture"
- "Fire reported in apartment building, smoke visible from multiple floors"
- "Traffic accident: two-vehicle collision at Main St and Oak Ave intersection"
- "Domestic disturbance: loud argument and sounds of breaking glass"
- "Suspicious person attempting to break into a vehicle in mall parking lot"

## Project Structure

```
911-call-generator/
├── app.py                      # Main Flask application
├── config.py                   # Configuration management
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not in git)
├── .env.example               # Template for environment variables
├── .gitignore                 # Git ignore file
├── README.md                  # This file
├── static/
│   ├── css/
│   │   └── style.css         # Custom CSS
│   ├── js/
│   │   └── main.js           # Frontend JavaScript
│   └── audio/                # Generated audio files (temporary)
├── templates/
│   ├── base.html             # Base template
│   └── index.html            # Main form page
├── services/
│   ├── gemini_service.py     # Google Gemini integration
│   ├── elevenlabs_service.py # ElevenLabs TTS integration
│   └── audio_processor.py    # Audio processing
└── utils/
    ├── validators.py          # Input validation
    └── file_manager.py        # File handling
```

## API Endpoints

### GET `/`
Main application page with the form interface.

### POST `/generate`
Generate 911 call audio from prompt.

**Parameters**:
- `prompt` (string): Emergency scenario description
- `audio_format` (string): 'mp3' or 'wav'
- `diarized` (string): 'true' or 'false'

**Response**:
```json
{
  "success": true,
  "audio_url": "/download/call_20260112_143052_a1b2c3d4.mp3",
  "filename": "call_20260112_143052_a1b2c3d4.mp3",
  "duration": 45.3,
  "exchanges": 10,
  "metadata": {
    "scenario_type": "traffic",
    "urgency_level": "high"
  },
  "diarized": false,
  "format": "mp3"
}
```

### GET `/download/<filename>`
Download generated audio file.

### GET `/health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "911 Call Generator",
  "gemini_configured": true,
  "elevenlabs_configured": true,
  "dispatcher_voice_configured": true,
  "caller_voice_configured": true
}
```

## Configuration

The application can be configured via environment variables in the `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |
| `DISPATCHER_VOICE_ID` | ElevenLabs voice ID for dispatcher | Yes |
| `CALLER_VOICE_ID` | ElevenLabs voice ID for caller | Yes |

Additional settings can be modified in `config.py`:
- `MAX_PROMPT_LENGTH`: Maximum prompt length (default: 500)
- `AUDIO_FILE_LIFETIME`: How long to keep generated files in seconds (default: 3600)

## Troubleshooting

### "Missing required configuration" error
- Make sure your `.env` file exists and contains all required API keys
- Check that the API keys are valid and not expired

### "Failed to generate dialogue" error
- Verify your Google Gemini API key is correct
- Check your API quota hasn't been exceeded
- Ensure you have internet connectivity

### "Failed to generate speech" error
- Verify your ElevenLabs API key is correct
- Check your ElevenLabs character quota
- Ensure the voice IDs are valid

### Audio processing errors
- Make sure ffmpeg is installed: `ffmpeg -version`
- Check that you have write permissions in the `static/audio/` directory

### Import errors
- Ensure virtual environment is activated
- Reinstall dependencies: `pip install -r requirements.txt`

## Development

### Running in Development Mode

The application runs in debug mode by default when started with `python app.py`.

### Running in Production

For production deployment, use Gunicorn:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Security Considerations

- Never commit your `.env` file to version control
- Use strong, unique API keys
- The application includes input validation and sanitization
- Generated audio files are automatically cleaned up after 1 hour
- File download paths are validated to prevent directory traversal attacks

## Limitations

- Maximum prompt length: 500 characters
- Generated calls are typically 20-60 seconds long
- Requires active API keys with sufficient quota
- Audio generation time: 10-30 seconds per call

## License

This project is for educational and testing purposes only. Do not use for actual emergency services or to create misleading emergency recordings.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the application logs in the console
3. Verify your API keys and configurations

## Credits

- **Flask**: Web framework
- **Google Gemini**: Dialogue generation
- **ElevenLabs**: Text-to-speech
- **pydub**: Audio processing
- **Bootstrap**: Frontend UI framework
