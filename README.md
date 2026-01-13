# 911 Call Generator

A Flask web application that generates realistic 911 emergency call audio from text prompts. The application uses Google Gemini for dialogue generation and ElevenLabs for high-quality text-to-speech conversion.

## Purpose

This tool is designed for testing and training purposes, allowing developers and trainers to generate realistic 911 call audio without needing actual emergency recordings.

## Features

### Call Types
- **Emergency Call (Dispatcher ↔ Caller)**: Standard 911 emergency call with dispatcher and caller
- **Dispatcher Transfer (Dispatcher ↔ Dispatcher)**: Professional transfer between dispatchers or to supervisors
- **Warm Transfer to Nurse (Dispatcher → Nurse → Caller)**: 3-speaker medical triage scenarios where dispatcher transfers caller to nurse

### AI & Voice
- **AI-Generated Dialogue**: Uses Google Gemini to create realistic conversations with natural flow
- **High-Quality Voice Synthesis**: Leverages ElevenLabs TTS for natural-sounding audio
- **Voice Selection**: Choose from 25+ professional voices with real-time preview
- **Gender-Aware Generation**: Dialogue adapts to match selected voice genders and uses appropriate pronouns

### Caller Behavior Control
- **Emotion Control**: Adjust caller emotion level from calm to hysterical (5 levels)
- **Erratic Behavior Control**: Configure how difficult the caller is - from focused to highly erratic/incoherent (5 levels)
  - Control rambling, interrupting, going off-topic, and coherence
  - Perfect for training dispatchers to handle difficult callers

### Training Features
- **Protocol Questions**: Add specific questions that must be asked during calls
  - Separate protocol questions for dispatcher and nurse in warm transfers
  - Questions are naturally integrated into the conversation
  - Ideal for telecommunicator training and quality assurance

### Audio Options
- **Duration Control**: Set target call length from 30 seconds to 3 minutes
- **Multiple Audio Formats**: Export as MP3 or WAV
- **Diarization Option**: Create stereo audio with speakers on separate channels (useful for analysis)

### User Experience
- **Prompt History**: Save and reload previous generation settings (last 10 prompts)
- **Web Interface**: User-friendly browser-based interface with Bootstrap 5
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
   - Voices are selected directly in the web interface with preview functionality

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
   ```

   Note: Voice selection is done in the web interface, not in the `.env` file.

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

1. **Select Call Type**:
   - **Emergency Call**: Standard dispatcher-to-caller conversation
   - **Dispatcher Transfer**: Transfer between two dispatchers
   - **Warm Transfer to Nurse**: 3-speaker medical triage (dispatcher introduces caller to nurse)

2. **Enter a Scenario**: Describe the situation in the text area
   - Example: "Car accident on Highway 101 with multiple injuries"
   - For warm transfers: "Caller experiencing chest pain and shortness of breath"
   - Keep it under 500 characters

3. **Add Protocol Questions** (Optional):
   - Click "Add Protocol Questions" to expand this section
   - Enter specific questions that must be asked (one per line)
   - For warm transfers, you can set separate questions for dispatcher and nurse
   - Example dispatcher questions: "What is the exact address?", "Are there any weapons?"
   - Example nurse questions: "What medications are you taking?", "Do you have any allergies?"

4. **Select Voices**:
   - **Dispatcher Voice**: Choose from professional, calm voices
   - **Caller Voice** (or Second Dispatcher Voice): Choose from varied voices
   - **Nurse Voice** (warm transfer only): Choose a calm, professional voice
   - Click the **Preview** button to hear a sample of each voice before generating

5. **Set Call Duration**:
   - Choose target length from 30 seconds to 3 minutes
   - Longer durations generate more detailed conversations

6. **Choose Emotion Level** (Emergency/Warm Transfer only):
   - **Calm**: Composed and clear speech
   - **Concerned**: Worried but coherent (default)
   - **Anxious**: Nervous and stressed
   - **Panicked**: Very distressed and urgent
   - **Hysterical**: Extremely emotional
   - This affects both dialogue content and voice characteristics

7. **Configure Erratic Behavior** (Emergency/Warm Transfer only):
   - **None**: Focused and coherent (default)
   - **Slight**: Minor rambling or tangents
   - **Moderate**: Some difficulty staying on topic
   - **High**: Frequent interruptions and tangents
   - **Extreme**: Very difficult to manage, highly incoherent
   - Perfect for training on handling difficult callers

8. **Select Audio Format**:
   - **MP3**: Compressed format, smaller file size
   - **WAV**: Uncompressed format, higher quality

9. **Enable Diarization** (optional):
   - Check this box to create stereo audio with speakers on separate channels
   - Useful for analysis or processing tools that need speaker separation
   - For 2-speaker calls: Speaker 1 on left, Speaker 2 on right

10. **Click "Generate Call"**: The process takes 10-30 seconds depending on dialogue length

11. **Play and Download**: Once generated, you can play the audio in the browser or download it

12. **Use History**: Your recent prompts are saved and can be reloaded with the "Load" button

### Example Scenarios

**Emergency Calls (Dispatcher ↔ Caller):**
- "Medical emergency: elderly person fell and can't get up, possible hip fracture"
- "Fire reported in apartment building, smoke visible from multiple floors"
- "Traffic accident: two-vehicle collision at Main St and Oak Ave intersection"
- "Domestic disturbance: loud argument and sounds of breaking glass"
- "Suspicious person attempting to break into a vehicle in mall parking lot"

**Dispatcher Transfers (Dispatcher ↔ Dispatcher):**
- "Active structure fire at 2455 Oak Street, two-alarm response, transferring to Battalion Chief"
- "Armed robbery in progress at convenience store, multiple suspects, transferring to SWAT commander"
- "Multi-vehicle accident on I-95 with entrapment, transferring to fire operations"
- "Missing child case with possible abduction, transferring to detective unit"

**Warm Transfers to Nurse (Dispatcher → Nurse → Caller):**
- "Caller experiencing severe chest pain radiating to left arm, shortness of breath"
- "Possible stroke: sudden weakness on one side, slurred speech, confusion"
- "Difficulty breathing, history of asthma, ran out of inhaler medication"
- "High fever with severe headache and stiff neck, possible meningitis"
- "Diabetic emergency: confusion, sweating, shaking"

### Sample Configurations

Here are some tested configurations you can try:

**Basic Emergency Call:**
- **Call Type**: Emergency Call
- **Prompt**: "Car accident on Highway 101 with multiple injuries"
- **Duration**: 60 seconds
- **Emotion**: Concerned
- **Erratic Level**: None

**High-Stress Traffic Accident:**
- **Call Type**: Emergency Call
- **Prompt**: "Car accident on Highway 101"
- **Duration**: 60 seconds
- **Emotion**: Concerned
- **Erratic Level**: High (caller difficult to keep focused)

**Critical Medical Emergency:**
- **Call Type**: Emergency Call
- **Prompt**: "Possible heart attack, chest pain"
- **Duration**: 60 seconds
- **Emotion**: Panicked
- **Erratic Level**: Extreme (highly incoherent, jumping topics)

**Dispatcher Transfer with Protocol:**
- **Call Type**: Dispatcher Transfer
- **Prompt**: "Active structure fire at 2455 Oak Street, two-alarm response, multiple units on scene. Fire has spread to adjacent building."
- **Duration**: 60 seconds
- **Protocol Questions**:
  - What is the current status of evacuation?
  - How many units are currently on scene?
  - Are there any special hazards?

**Emergency Call with Protocol Questions:**
- **Call Type**: Emergency Call
- **Prompt**: "Car accident on Highway 101 with injuries"
- **Duration**: 60 seconds
- **Emotion**: Concerned
- **Dispatcher Protocol Questions**:
  - What is the exact mile marker?
  - How many vehicles are involved?
  - Are there any hazards on the road?

**Warm Transfer to Nurse with Dual Protocols:**
- **Call Type**: Warm Transfer to Nurse
- **Prompt**: "Caller experiencing severe chest pain radiating to left arm, shortness of breath. Started 20 minutes ago. Has history of high blood pressure."
- **Duration**: 90 seconds
- **Emotion**: Anxious
- **Erratic Level**: Slight
- **Dispatcher Protocol Questions**:
  - What is the caller's phone number?
  - What is the caller's location?
- **Nurse Protocol Questions**:
  - On a scale of 1-10, how severe is the pain?
  - Are you currently taking any medications?
  - Do you have any known allergies?

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
- `call_type` (string): Type of call - 'emergency', 'transfer', or 'warm_transfer'
- `call_duration` (integer): Target duration in seconds (30-180)
- `emotion_level` (string): Caller emotion level ('calm', 'concerned', 'anxious', 'panicked', 'hysterical')
- `erratic_level` (string): Caller erratic behavior level ('none', 'slight', 'moderate', 'high', 'extreme')
- `dispatcher_protocol_questions` (string): Optional protocol questions for dispatcher (one per line)
- `nurse_protocol_questions` (string): Optional protocol questions for nurse (one per line, warm_transfer only)
- `audio_format` (string): 'mp3' or 'wav'
- `diarized` (string): 'true' or 'false'
- `dispatcher_voice_id` (string): ElevenLabs voice ID for dispatcher
- `caller_voice_id` (string): ElevenLabs voice ID for caller
- `nurse_voice_id` (string): ElevenLabs voice ID for nurse (warm_transfer only)

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

### GET `/api/voices`
Get list of available ElevenLabs voices.

**Response**:
```json
{
  "success": true,
  "voices": [
    {
      "voice_id": "21m00Tcm4TlvDq8ikWAM",
      "name": "Rachel",
      "category": "premade",
      "description": "Professional female voice",
      "labels": {"gender": "female"},
      "preview_url": "https://..."
    }
  ]
}
```

### POST `/api/preview-voice`
Generate a preview audio sample for a voice.

**Parameters**:
```json
{
  "voice_id": "21m00Tcm4TlvDq8ikWAM",
  "sample_text": "Optional custom preview text"
}
```

**Response**: Audio file (audio/mpeg)

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
  "elevenlabs_configured": true
}
```

## Configuration

The application can be configured via environment variables in the `.env` file:

| Variable | Description | Required |
|----------|-------------|----------|
| `SECRET_KEY` | Flask secret key | Yes |
| `GEMINI_API_KEY` | Google Gemini API key | Yes |
| `ELEVENLABS_API_KEY` | ElevenLabs API key | Yes |

Additional settings can be modified in `config.py`:
- `MAX_PROMPT_LENGTH`: Maximum prompt length (default: 500)
- `AUDIO_FILE_LIFETIME`: How long to keep generated files in seconds (default: 3600)

Note: Voice IDs are selected through the web interface and are not stored in configuration.

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
- Call duration range: 30 seconds to 3 minutes
- Requires active API keys with sufficient quota
- Audio generation time: 10-30 seconds per call
- Voice preview and selection requires internet connectivity
- History stored in browser localStorage (limited to 10 recent prompts)

## License

This project is for educational and testing purposes only. Do not use for actual emergency services or to create misleading emergency recordings.

## Support

For issues or questions:
1. Check the Troubleshooting section above
2. Review the application logs in the console
3. Verify your API keys and configurations

## Recent Updates

### New Call Types & Scenarios
- **Warm Transfer to Nurse**: 3-speaker medical triage scenarios (dispatcher, nurse, caller)
- **Dispatcher Transfer**: Professional transfer scenarios between dispatchers
- **Call Type Selection**: Choose between emergency, transfer, and warm transfer scenarios
- Dynamic UI that adapts based on selected call type

### Advanced Training Features
- **Protocol Questions**: Add specific questions that must be asked during calls
  - Separate protocol questions for dispatcher and nurse in warm transfers
  - Questions naturally integrated into dialogue
  - Perfect for telecommunicator training and quality assurance
- **Erratic Behavior Control**: Configure caller difficulty from focused to highly erratic (5 levels)
  - Control rambling, interrupting, going off-topic, and coherence
  - Independent from emotion level for precise scenario control
  - Ideal for training on difficult caller management

### Voice & Audio Improvements
- Dynamic voice selection with 25+ voices
- Real-time voice preview before generation
- Gender-aware dialogue generation with proper pronouns
- Third voice support for warm transfer scenarios (nurse)
- Fixed "911" pronunciation (now "nine one one" instead of "nine eleven")
- Cleaned markdown formatting from TTS output

### User Experience
- Call duration selector (30s to 3 minutes)
- Caller emotion control (5 levels: calm to hysterical)
- Erratic behavior control (5 levels: none to extreme)
- Collapsible protocol questions section
- Prompt history with save/load functionality (last 10 prompts)
- Context-aware labels and help text based on call type
- Fixed form state persistence issues

### Technical Enhancements
- Voice stability adjustment based on emotion level
- Nurse voice generation with professional, calm tone
- Gender detection from ElevenLabs API
- Context-aware prompt engineering for LLM with behavior modifiers
- LocalStorage-based history management with backward compatibility
- Enhanced text preprocessing for cleaner speech
- XSS protection for user input
- Support for 3-speaker dialogue validation

## Credits

- **Flask**: Web framework
- **Google Gemini**: AI dialogue generation (gemini-2.5-flash model)
- **ElevenLabs**: High-quality text-to-speech
- **pydub**: Audio processing and manipulation
- **Bootstrap 5**: Responsive frontend UI framework
- **jQuery**: DOM manipulation and AJAX
