# 911 Call Generator - Project Documentation

## Overview
AI-powered training tool that generates realistic 911 emergency call audio for dispatcher training and testing purposes.

## Current Features

### Call Types
1. **Emergency Call** - Standard dispatcher-to-caller scenario
2. **Dispatcher Transfer** - Dispatcher-to-dispatcher handoff
3. **Warm Transfer to Nurse** - 3-way call with dispatcher, caller, and triage nurse
4. **Emergency Call with Translator** - 3-way call with language barrier (dispatcher, caller, bilingual translator)

### Multi-Language Support
- 12 languages supported: English, Spanish, French, German, Italian, Portuguese, Polish, Hindi, Japanese, Korean, Chinese (Mandarin), Arabic
- **Translator Scenario**: Dispatcher and caller speak different languages with professional translator facilitating
- ElevenLabs automatically switches between monolingual and multilingual models

### Audio Features
- **Voice Selection**: Choose from 28+ ElevenLabs voices for dispatcher, caller, and nurse/translator
- **Audio Quality Settings**: High, Medium, Low (phone quality), Very Low (poor connection)
- **Background Noise**: Traffic, Dispatch Center, Crowd, Sirens, Wind (with adjustable levels)
- **Diarized Audio**: Separate speakers on stereo channels (dispatcher left, caller right)
- **Audio Formats**: MP3, WAV

### Script Options
- **AI Generation**: Gemini generates dialogue based on scenario description
- **Pre-loaded Scripts**: 20 sample call transcripts from `/sample_scripts/` directory
- **Protocol Questions**: Custom required questions for dispatcher or nurse

### Caller Behavior Controls
- **Emotion Levels**: Calm, Concerned, Anxious, Panicked, Hysterical
- **Erratic Behavior**: None to Extreme (rambling, interrupting, going off-topic)

### UI Features
- **Collapsible Recent Prompts**: History with relative timestamps ("5 minutes ago")
- **"How it works" Modal**: Accessible from navbar instead of static section
- **Voice Preview**: Test voices before generating
- **Call Type Adaptive UI**: Shows/hides relevant controls based on scenario

## Technical Stack

### Backend
- **Framework**: Flask (Python)
- **AI/LLM**: Google Gemini 2.5 Flash (dialogue generation)
- **TTS**: ElevenLabs API (text-to-speech)
- **Audio Processing**: pydub (AudioSegment manipulation)

### Frontend
- **UI Framework**: Bootstrap 5
- **JavaScript**: jQuery
- **Icons**: Bootstrap Icons

### Key Python Dependencies
- `google-generativeai` - Gemini API
- `elevenlabs` - TTS API
- `pydub` - Audio processing
- `flask` - Web framework

## Project Structure

```
911-call-generator/
├── app.py                          # Main Flask application
├── services/
│   ├── gemini_service.py          # Dialogue generation
│   ├── elevenlabs_service.py      # Text-to-speech
│   └── audio_processor.py         # Audio mixing and effects
├── utils/
│   └── script_loader.py           # Pre-loaded script handling
├── templates/
│   ├── base.html                  # Base template with navbar
│   └── index.html                 # Main form and UI
├── static/
│   ├── css/style.css              # Custom styles
│   ├── js/main.js                 # Frontend logic
│   ├── audio/                     # Generated call output
│   └── ambient/                   # Background noise samples
├── sample_scripts/                # Pre-made call transcripts (20 files)
└── venv/                          # Python virtual environment
```

## Key Architecture Decisions

### Translator Scenario Implementation
- Translator joins call after dispatcher recognizes language barrier
- Dispatcher explicitly brings translator in as a known resource ("Let me connect our translator")
- Translator speaks both languages, alternating based on audience
- Uses `speaker: "translator"` in dialogue JSON
- Audio generation uses multilingual model for translator voice

### Voice Defaults
- **Dispatcher**: Roger (or Rachel, Antoni, Arnold)
- **Caller**: River (or Bella, Adam, Elli)
- **Nurse/Translator**: Sophie (or Sarah, Grace, Domi)

### Audio Quality Defaults
- Default set to **Low** for realistic phone quality
- Background noise samples loaded from `/static/ambient/` with fallback to tone synthesis

### Pre-loaded Scripts
- When selected, hides scenario configuration (call type, duration, emotion, protocol)
- Only shows language and voice settings
- Loads from 20 transcript files in `/sample_scripts/`

## Recent Major Changes

### Session 2 (January 14, 2026)
1. **Translator Scenario Added**
   - New call type with separate language selectors
   - Dispatcher brings translator in as professional service
   - 3-speaker dialogue with language barrier

2. **UI Reorganization**
   - Call Type & Duration moved to first row (6 cols each)
   - Language section gets dedicated full-width row
   - Diarized checkbox moved to top, made compact
   - "How it works" moved to navbar modal

3. **Recent Prompts Enhancement**
   - Made collapsible by default
   - Added relative timestamps ("5 minutes ago")
   - Hover shows full timestamp
   - Better call type badges (including Translator)

4. **Default Voice Updates**
   - Audio quality: High → Low (phone quality)
   - Caller voice: River prioritized
   - Nurse/Translator voice: Sophie prioritized

5. **Cache Busting**
   - Added version parameter to JS imports (`?v=TIMESTAMP`)
   - Ensures browser loads latest changes

### Session 1 (Prior to January 14, 2026)
- Background noise system with real audio samples
- Pre-loaded script feature
- Multi-language support (12 languages)
- UI layout optimizations

## Configuration

### Environment Variables (.env)
```bash
GEMINI_API_KEY=your_gemini_api_key
ELEVENLABS_API_KEY=your_elevenlabs_api_key
```

### Audio Settings
- Sample rate: 44100 Hz (high), 24000 Hz (medium), 16000 Hz (low), 8000 Hz (very low)
- Background noise samples: 6 files in `/static/ambient/`
- Audio output: `/static/audio/call_YYYYMMDD_HHMMSS_*.mp3`

## Known Issues / TODOs

### Current
- None critical

### Future Enhancements
- [ ] Support for more languages
- [ ] Custom voice cloning integration
- [ ] Multi-call scenario support (series of related calls)
- [ ] Analytics dashboard for generated calls
- [ ] Export dialogue transcripts as text
- [ ] Audio waveform visualization

## Development Workflow

### Setup
```bash
cd /Users/cfucci/Desktop/911-call-generator
source venv/bin/activate
python app.py
```

### Git Workflow
```bash
git add .
git commit -m "Description"
git push origin main
```

### Debugging
- Flask runs in debug mode (auto-reload on file changes)
- Check console logs for voice selection: "Selected nurse/translator voice: ..."
- Browser console (F12) for frontend debugging

## API Usage

### Gemini
- Model: `gemini-2.5-flash`
- Generates JSON dialogue structure with speaker, text, and pause_after fields
- Language-specific prompts for non-English scenarios

### ElevenLabs
- Uses `eleven_monolingual_v1` for English
- Uses `eleven_multilingual_v2` for other languages and translator scenarios
- Voice streaming with `generate()` function

## Testing
- Test translator scenarios with different language combinations
- Verify voice defaults load correctly (check console)
- Test pre-loaded script selection (UI should hide scenario config)
- Test collapsible history with relative timestamps

## Maintenance Notes

### When Adding New Features
1. Update this PROJECT_NOTES.md
2. Add version parameter to base.html if JS changes (`?v=TIMESTAMP`)
3. Test in incognito window to verify no cache issues
4. Update README.md if user-facing changes

### Common Issues
- **Voice not selecting correctly**: Check console log, ensure voice exists in ElevenLabs account
- **Browser caching JS/CSS**: Update version parameter in base.html
- **Port 5000 in use**: `lsof -ti:5000 | xargs kill -9`

## Repository
https://github.com/cfuccisos/911-call-generator

Last Updated: January 14, 2026
