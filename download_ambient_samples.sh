#!/bin/bash

# Download ambient audio samples for 911 Call Generator
# Run this script from the project root directory

AMBIENT_DIR="static/audio/ambient"
cd "$(dirname "$0")"

echo "Downloading ambient audio samples..."
echo "This may take a few minutes..."

# Create directory if it doesn't exist
mkdir -p "$AMBIENT_DIR"
cd "$AMBIENT_DIR"

# Download from Mixkit (no attribution required, free to use)
echo ""
echo "📥 Downloading crowd sounds..."
curl -L "https://assets.mixkit.co/active_storage/sfx/2490/2490.wav" -o "crowd-murmur-temp.wav" 2>&1 | grep -E "(%)$" || echo "✓ Downloaded crowd sound"

echo ""
echo "📥 Downloading traffic sounds..."
curl -L "https://assets.mixkit.co/active_storage/sfx/2494/2494.wav" -o "traffic-road-temp.wav" 2>&1 | grep -E "(%)$" || echo "✓ Downloaded traffic sound"

echo ""
echo "📥 Downloading siren sounds..."
curl -L "https://assets.mixkit.co/active_storage/sfx/1635/1635.wav" -o "emergency-sirens-temp.wav" 2>&1 | grep -E "(%)$" || echo "✓ Downloaded siren sound"

echo ""
echo "📥 Downloading dispatch/office ambience..."
curl -L "https://assets.mixkit.co/active_storage/sfx/2506/2506.wav" -o "dispatch-center-temp.wav" 2>&1 | grep -E "(%)$" || echo "✓ Downloaded dispatch sound"

echo ""
echo "📥 Downloading wind sounds..."
curl -L "https://assets.mixkit.co/active_storage/sfx/39/39.wav" -o "wind-outdoor-temp.wav" 2>&1 | grep -E "(%)$" || echo "✓ Downloaded wind sound"

echo ""
echo "Converting WAV files to MP3 for better file size..."

# Convert to MP3 and rename
for file in *-temp.wav; do
    if [ -f "$file" ]; then
        basename="${file%-temp.wav}"
        echo "Converting $basename..."
        ffmpeg -i "$file" -acodec libmp3lame -ab 192k "${basename}.mp3" -y 2>&1 | grep -E "time=" || echo "✓ Converted $basename"
        rm "$file"
    fi
done

echo ""
echo "✅ Download complete!"
echo ""
echo "Downloaded files:"
ls -lh *.mp3 2>/dev/null || ls -lh *.wav 2>/dev/null || echo "No files downloaded successfully"

echo ""
echo "================================================"
echo "IMPORTANT: Manual Download Instructions"
echo "================================================"
echo ""
echo "If some downloads failed, you can manually download from these sources:"
echo ""
echo "🔹 Mixkit (No signup, no attribution):"
echo "   https://mixkit.co/free-sound-effects/crowd/"
echo "   https://mixkit.co/free-sound-effects/traffic/"
echo "   https://mixkit.co/free-sound-effects/siren/"
echo ""
echo "🔹 Pixabay (No attribution):"
echo "   https://pixabay.com/sound-effects/search/crowd%20talking/"
echo "   https://pixabay.com/sound-effects/search/traffic/"
echo "   https://pixabay.com/sound-effects/search/sirens/"
echo ""
echo "🔹 Freesound (Requires free account):"
echo "   https://freesound.org/search/?q=crowd+murmur"
echo "   https://freesound.org/search/?q=dispatch+radio"
echo "   https://freesound.org/search/?q=traffic"
echo ""
echo "Required filenames (place in $AMBIENT_DIR):"
echo "  - crowd-murmur.mp3      (crowd talking/restaurant ambience)"
echo "  - dispatch-center.mp3   (dispatch radio with background chatter)"
echo "  - traffic-road.mp3      (traffic/road noise)"
echo "  - emergency-sirens.mp3  (distant emergency sirens)"
echo "  - wind-outdoor.mp3      (wind sounds)"
echo "  - phone-static.mp3      (phone static - optional)"
echo ""
