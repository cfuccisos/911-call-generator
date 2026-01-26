FROM python:3.11-slim

# Install system dependencies
# ffmpeg is required for pydub audio processing
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Expose port 8080 (App Runner default)
EXPOSE 8080

# Copy requirements first for better layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY config.py .
COPY services/ ./services/
COPY templates/ ./templates/
COPY static/ ./static/
COPY utils/ ./utils/
COPY sample_scripts/ ./sample_scripts/

# Create directory for generated audio files
RUN mkdir -p static/audio

# Use gunicorn for production serving
# - bind to 0.0.0.0:8080 for App Runner
# - 2 worker processes (can be adjusted based on resources)
# - timeout of 300 seconds (calls can take time to generate)
# - access log to stdout for CloudWatch
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "300", "--access-logfile", "-", "app:app"]
