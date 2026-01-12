"""911 Call Generator - Flask Application

A web application that generates realistic 911 call audio from text prompts
using Google Gemini for dialogue generation and ElevenLabs for text-to-speech.
"""

from flask import Flask, render_template, request, jsonify, send_file
from config import Config
from services.gemini_service import GeminiService
from services.elevenlabs_service import ElevenLabsService
from services.audio_processor import AudioProcessor
from utils.validators import validate_prompt, validate_audio_format
from utils.file_manager import FileManager
import logging

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Validate configuration
try:
    Config.validate()
    logger.info("Configuration validated successfully")
except ValueError as e:
    logger.error(f"Configuration error: {e}")
    logger.error("Please ensure your .env file is properly configured")

# Initialize services
gemini = GeminiService(app.config['GEMINI_API_KEY'])
elevenlabs = ElevenLabsService(app.config['ELEVENLABS_API_KEY'])
audio_processor = AudioProcessor()
file_manager = FileManager(app.config['AUDIO_OUTPUT_DIR'])


@app.route('/')
def index():
    """Render the main page with the form."""
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate():
    """
    Generate 911 call audio from user prompt.

    Expected form data:
        - prompt: Text description of emergency scenario
        - audio_format: 'mp3' or 'wav'
        - diarized: 'true' or 'false'

    Returns:
        JSON with audio_url, filename, duration, and metadata
    """
    try:
        # 1. Get and validate input
        prompt = request.form.get('prompt', '').strip()
        protocol_questions = request.form.get('protocol_questions', '').strip()
        call_duration_str = request.form.get('call_duration', '60').strip()
        call_duration = int(call_duration_str) if call_duration_str else 60
        emotion_level = request.form.get('emotion_level', 'concerned').strip()
        audio_format = request.form.get('audio_format', 'mp3').lower()
        diarized = request.form.get('diarized', 'false').lower() == 'true'
        dispatcher_voice_id = request.form.get('dispatcher_voice_id', '').strip()
        caller_voice_id = request.form.get('caller_voice_id', '').strip()

        logger.info(f"Generate request: format={audio_format}, diarized={diarized}, duration={call_duration}s, emotion={emotion_level}")
        logger.info(f"Voices: dispatcher={dispatcher_voice_id[:20]}..., caller={caller_voice_id[:20]}...")
        logger.info(f"Prompt: {prompt[:100]}...")
        if protocol_questions:
            logger.info(f"Protocol questions: {protocol_questions[:100]}...")

        # Validate prompt
        is_valid, error_msg = validate_prompt(
            prompt,
            max_length=app.config['MAX_PROMPT_LENGTH']
        )
        if not is_valid:
            return jsonify({"error": error_msg}), 400

        # Validate audio format
        if not validate_audio_format(
            audio_format,
            allowed_formats=app.config['ALLOWED_AUDIO_FORMATS']
        ):
            return jsonify(
                {"error": f"Invalid audio format. Must be mp3 or wav"}
            ), 400

        # Validate voice IDs
        if not dispatcher_voice_id or not caller_voice_id:
            return jsonify(
                {"error": "Both dispatcher and caller voices must be selected"}
            ), 400

        # Get voice information including gender
        dispatcher_info = elevenlabs.get_voice_info(dispatcher_voice_id)
        caller_info = elevenlabs.get_voice_info(caller_voice_id)

        logger.info(f"Dispatcher voice: {dispatcher_info['name']} ({dispatcher_info['gender']})")
        logger.info(f"Caller voice: {caller_info['name']} ({caller_info['gender']})")

        # 2. Generate dialogue with Gemini
        logger.info("Step 1: Generating dialogue...")
        dialogue_data = gemini.generate_dialogue(
            prompt,
            call_duration,
            emotion_level,
            dispatcher_info['gender'],
            caller_info['gender'],
            protocol_questions
        )
        dialogue = dialogue_data['dialogue']
        metadata = dialogue_data.get('metadata', {})

        logger.info(f"Generated {len(dialogue)} dialogue exchanges")

        # 3. Generate speech for each line with ElevenLabs
        logger.info("Step 2: Generating speech audio...")
        audio_segments = []

        for i, item in enumerate(dialogue):
            # Get appropriate voice ID from form data
            if item['speaker'] == 'dispatcher':
                audio_bytes = elevenlabs.generate_dispatcher_audio(
                    item['text'],
                    dispatcher_voice_id
                )
            else:  # caller
                audio_bytes = elevenlabs.generate_caller_audio(
                    item['text'],
                    caller_voice_id,
                    emotion_level
                )

            audio_segments.append(audio_bytes)
            logger.info(
                f"Generated audio {i+1}/{len(dialogue)}: "
                f"{item['speaker']} - {item['text'][:30]}..."
            )

        # 4. Process audio (combine or diarize)
        logger.info("Step 3: Processing audio...")
        if diarized:
            logger.info("Creating diarized audio (stereo channels)")
            final_audio = audio_processor.create_diarized_audio(
                dialogue,
                audio_segments
            )
        else:
            logger.info("Creating combined audio (mono)")
            final_audio = audio_processor.combine_dialogue_audio(
                dialogue,
                audio_segments
            )

        # 5. Save file
        logger.info("Step 4: Saving audio file...")
        filename = file_manager.generate_unique_filename(audio_format)
        filepath = file_manager.save_audio_file(
            final_audio,
            filename,
            audio_format
        )

        logger.info(f"Audio saved: {filepath}")

        # 6. Return response
        duration_seconds = len(final_audio) / 1000

        response_data = {
            "success": True,
            "audio_url": f"/download/{filename}",
            "filename": filename,
            "duration": round(duration_seconds, 2),
            "exchanges": len(dialogue),
            "metadata": metadata,
            "diarized": diarized,
            "format": audio_format
        }

        logger.info(f"Successfully generated call: {duration_seconds:.1f}s")
        return jsonify(response_data)

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        return jsonify({"error": str(e)}), 400

    except Exception as e:
        logger.error(f"Error generating call: {str(e)}", exc_info=True)
        return jsonify({
            "error": "Failed to generate call. Please try again."
        }), 500


@app.route('/download/<filename>')
def download(filename):
    """
    Download generated audio file.

    Args:
        filename: Name of the audio file

    Returns:
        File for download
    """
    try:
        filepath = file_manager.get_file_path(filename)
        return send_file(filepath, as_attachment=True)
    except FileNotFoundError:
        logger.error(f"File not found: {filename}")
        return jsonify({"error": "File not found"}), 404
    except ValueError as e:
        logger.error(f"Invalid filename: {filename}")
        return jsonify({"error": "Invalid filename"}), 400


@app.route('/health')
def health():
    """
    Health check endpoint.

    Returns:
        JSON with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "911 Call Generator",
        "gemini_configured": bool(app.config['GEMINI_API_KEY']),
        "elevenlabs_configured": bool(app.config['ELEVENLABS_API_KEY'])
    })


@app.route('/api/voices')
def get_voices():
    """
    Get list of available voices from ElevenLabs.

    Returns:
        JSON with list of voices
    """
    try:
        voices_list = elevenlabs.get_available_voices()
        return jsonify({
            "success": True,
            "voices": voices_list
        })
    except Exception as e:
        logger.error(f"Error fetching voices: {str(e)}")
        return jsonify({
            "error": "Failed to fetch voices"
        }), 500


@app.route('/api/preview-voice', methods=['POST'])
def preview_voice():
    """
    Generate voice preview audio.

    Expected JSON data:
        - voice_id: ElevenLabs voice ID
        - sample_text: Optional custom preview text

    Returns:
        Audio file for preview
    """
    try:
        data = request.get_json()
        voice_id = data.get('voice_id')

        if not voice_id:
            return jsonify({"error": "voice_id is required"}), 400

        sample_text = data.get('sample_text')

        # Generate preview audio
        audio_bytes = elevenlabs.generate_preview(voice_id, sample_text)

        # Return audio directly
        from io import BytesIO
        from flask import Response

        return Response(
            audio_bytes,
            mimetype='audio/mpeg',
            headers={
                'Content-Disposition': f'inline; filename=preview_{voice_id}.mp3'
            }
        )

    except Exception as e:
        logger.error(f"Error generating preview: {str(e)}")
        return jsonify({
            "error": "Failed to generate preview"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal error: {error}")
    return jsonify({"error": "Internal server error"}), 500


if __name__ == '__main__':
    # Cleanup old files on startup
    logger.info("Cleaning up old audio files...")
    file_manager.cleanup_old_files(app.config.get('AUDIO_FILE_LIFETIME', 3600))

    # Run app
    logger.info("Starting 911 Call Generator...")
    logger.info("Access the application at: http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)
