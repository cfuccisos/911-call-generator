"""Script loader utility for loading pre-made call transcripts."""

import os
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class ScriptLoader:
    """Loads and parses pre-made call transcript files."""

    def __init__(self, scripts_dir: str):
        """
        Initialize ScriptLoader.

        Args:
            scripts_dir: Path to directory containing script .txt files
        """
        self.scripts_dir = scripts_dir
        self.logger = logging.getLogger(__name__)

    def list_available_scripts(self) -> List[Dict[str, str]]:
        """
        List all available script files.

        Returns:
            List of dicts with 'filename', 'title', and 'description'
        """
        if not os.path.exists(self.scripts_dir):
            self.logger.warning(f"Scripts directory not found: {self.scripts_dir}")
            return []

        scripts = []
        try:
            for filename in sorted(os.listdir(self.scripts_dir)):
                if filename.endswith('.txt'):
                    filepath = os.path.join(self.scripts_dir, filename)

                    # Read first line for title
                    with open(filepath, 'r', encoding='utf-8') as f:
                        first_line = f.readline().strip()

                    # Extract title (remove leading number and whitespace)
                    # Format: "1. Domestic violence / active disturbance"
                    title = first_line.split('.', 1)[-1].strip() if '.' in first_line else first_line

                    # Create description from filename
                    description = filename.replace('call_', '').replace('.txt', '').replace('_', ' ').title()

                    scripts.append({
                        'filename': filename,
                        'title': title,
                        'description': description
                    })
        except Exception as e:
            self.logger.error(f"Error listing scripts: {e}")

        return scripts

    def load_script(self, filename: str) -> Optional[Dict]:
        """
        Load and parse a script file.

        Args:
            filename: Name of the script file to load

        Returns:
            Dict with 'title' and 'dialogue' list, or None if error
        """
        filepath = os.path.join(self.scripts_dir, filename)

        if not os.path.exists(filepath):
            self.logger.error(f"Script file not found: {filepath}")
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # First line is the title
            title = lines[0].strip()
            if '.' in title:
                title = title.split('.', 1)[-1].strip()

            # Parse dialogue lines
            dialogue = []
            for line in lines[1:]:
                line = line.strip()
                if not line:
                    continue

                # Parse "Speaker: text" format
                if ':' in line:
                    speaker_part, text = line.split(':', 1)
                    speaker = speaker_part.strip().lower()
                    text = text.strip()

                    # Normalize speaker names
                    if 'dispatcher' in speaker:
                        speaker = 'dispatcher'
                    elif 'caller' in speaker:
                        speaker = 'caller'
                    else:
                        # Default to caller for unknown speakers
                        speaker = 'caller'

                    # Add pause based on speaker and position
                    # Dispatcher typically has shorter pauses
                    pause_after = 0.5 if speaker == 'dispatcher' else 0.8

                    dialogue.append({
                        'speaker': speaker,
                        'text': text,
                        'pause_after': pause_after
                    })

            if not dialogue:
                self.logger.error(f"No dialogue found in script: {filename}")
                return None

            self.logger.info(f"Loaded script '{title}' with {len(dialogue)} dialogue lines")

            return {
                'title': title,
                'dialogue': dialogue,
                'metadata': {
                    'scenario_type': 'preloaded',
                    'urgency_level': 'medium',
                    'source': filename
                }
            }

        except Exception as e:
            self.logger.error(f"Error loading script {filename}: {e}")
            return None
