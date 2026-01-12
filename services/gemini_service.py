"""Google Gemini service for dialogue generation."""

import google.generativeai as genai
import json
import logging


class GeminiService:
    """Service for generating 911 call dialogue using Google Gemini."""

    def __init__(self, api_key: str):
        """
        Initialize GeminiService.

        Args:
            api_key: Google Gemini API key
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.logger = logging.getLogger(__name__)

    def generate_dialogue(
        self,
        scenario: str,
        target_duration: int = 60,
        emotion_level: str = 'concerned',
        dispatcher_gender: str = 'unknown',
        caller_gender: str = 'unknown',
        protocol_questions: str = ''
    ) -> dict:
        """
        Generate 911 call dialogue based on scenario.

        Args:
            scenario: Description of the emergency scenario
            target_duration: Target call duration in seconds (default: 60)
            emotion_level: Caller emotion level (calm, concerned, anxious, panicked, hysterical)
            dispatcher_gender: Gender of dispatcher voice (male, female, unknown)
            caller_gender: Gender of caller voice (male, female, unknown)
            protocol_questions: Optional specific questions dispatcher must ask

        Returns:
            Dictionary with structure:
            {
                "dialogue": [
                    {"speaker": "dispatcher", "text": "...", "pause_after": 0.5},
                    {"speaker": "caller", "text": "...", "pause_after": 0.8},
                    ...
                ],
                "metadata": {
                    "scenario_type": "medical/fire/police/traffic",
                    "urgency_level": "low/medium/high/critical"
                }
            }

        Raises:
            ValueError: If dialogue generation or parsing fails
        """
        prompt = self._build_prompt(scenario, target_duration, emotion_level, dispatcher_gender, caller_gender, protocol_questions)

        try:
            protocol_msg = f", protocol: {len(protocol_questions.splitlines())} questions" if protocol_questions else ""
            self.logger.info(f"Generating dialogue for scenario: {scenario[:50]}... (target: {target_duration}s, emotion: {emotion_level}, dispatcher: {dispatcher_gender}, caller: {caller_gender}{protocol_msg})")
            response = self.model.generate_content(prompt)
            dialogue_data = self._parse_response(response.text)
            self.logger.info(f"Generated {len(dialogue_data['dialogue'])} dialogue exchanges")
            return dialogue_data
        except Exception as e:
            self.logger.error(f"Gemini API error: {str(e)}")
            raise ValueError(f"Failed to generate dialogue: {str(e)}")

    def _build_prompt(
        self,
        scenario: str,
        target_duration: int = 60,
        emotion_level: str = 'concerned',
        dispatcher_gender: str = 'unknown',
        caller_gender: str = 'unknown',
        protocol_questions: str = ''
    ) -> str:
        """
        Build prompt for Gemini to generate realistic 911 dialogue.

        Args:
            scenario: User's emergency scenario description
            target_duration: Target duration in seconds
            emotion_level: Caller emotion level
            dispatcher_gender: Gender of dispatcher
            caller_gender: Gender of caller
            protocol_questions: Optional specific questions to include

        Returns:
            Formatted prompt string
        """
        # Calculate suggested number of exchanges based on target duration
        # Rough estimate: average exchange is ~5-6 seconds (speech + pause)
        if target_duration <= 30:
            exchange_range = "4-6"
        elif target_duration <= 60:
            exchange_range = "8-12"
        elif target_duration <= 90:
            exchange_range = "12-16"
        elif target_duration <= 120:
            exchange_range = "16-20"
        else:  # 180+ seconds
            exchange_range = "24-30"

        # Map emotion level to description for prompt
        emotion_descriptions = {
            'calm': 'calm and composed, speaking clearly with minimal emotion',
            'concerned': 'worried but coherent, with some stress in their voice',
            'anxious': 'nervous and stressed, speaking quickly with noticeable worry',
            'panicked': 'very distressed, speaking urgently with fear and anxiety',
            'hysterical': 'extremely emotional, potentially crying or screaming, very difficult to calm'
        }
        emotion_desc = emotion_descriptions.get(emotion_level, emotion_descriptions['concerned'])

        # Build gender context for the prompt
        dispatcher_desc = ""
        if dispatcher_gender in ['male', 'female']:
            dispatcher_desc = f" The dispatcher is {dispatcher_gender}."

        caller_desc = ""
        if caller_gender in ['male', 'female']:
            caller_desc = f" The caller is {caller_gender}."

        gender_context = f"{dispatcher_desc}{caller_desc}" if (dispatcher_desc or caller_desc) else ""

        # Build protocol questions section if provided
        protocol_section = ""
        if protocol_questions:
            protocol_section = f"""

IMPORTANT - Protocol Questions:
The dispatcher MUST ask these specific questions during the call (integrate them naturally into the conversation):
{protocol_questions}
"""

        return f"""You are an expert in creating realistic 911 emergency call scenarios for training purposes.

Generate a dialogue between a 911 dispatcher and a caller based on this scenario:
{scenario}{protocol_section}

Requirements:
1. The dispatcher should be professional, calm, and ask relevant questions{dispatcher_desc}
2. The caller should be {emotion_desc}{caller_desc}
3. Include {exchange_range} exchanges total (target duration: ~{target_duration} seconds)
4. Dispatcher asks for: location, nature of emergency, injuries/hazards, etc.
5. Use appropriate pronouns and references based on the gender of each speaker
6. If protocol questions are provided above, ensure the dispatcher asks ALL of them naturally within the conversation
7. Format as JSON with this EXACT structure:

{{
  "dialogue": [
    {{"speaker": "dispatcher", "text": "911, what's your emergency?", "pause_after": 0.5}},
    {{"speaker": "caller", "text": "Help! There's been an accident!", "pause_after": 0.8}},
    {{"speaker": "dispatcher", "text": "Okay, I need you to stay calm. What's your location?", "pause_after": 0.6}},
    {{"speaker": "caller", "text": "We're on Highway 101, northbound near exit 25!", "pause_after": 0.7}}
  ],
  "metadata": {{
    "scenario_type": "medical/fire/police/traffic",
    "urgency_level": "low/medium/high/critical"
  }}
}}

Rules for pauses:
- Dispatcher pauses: 0.3-0.6 seconds (professional, quick responses)
- Caller pauses: 0.5-1.2 seconds (more emotional, varied)
- After questions: longer pauses (0.8-1.2 seconds) to allow thinking time

Important:
- Make the dialogue realistic and natural
- Include relevant details about the emergency
- The dispatcher should collect key information: location, nature, injuries, hazards
- The caller should sound appropriately stressed but coherent
- Return ONLY valid JSON, no additional text or explanation"""

    def _parse_response(self, response_text: str) -> dict:
        """
        Parse Gemini response and extract JSON dialogue.

        Args:
            response_text: Raw response text from Gemini

        Returns:
            Parsed dialogue dictionary

        Raises:
            ValueError: If parsing or validation fails
        """
        try:
            # Clean up response (remove markdown code blocks if present)
            cleaned = response_text.strip()

            # Remove markdown code block markers
            if cleaned.startswith('```'):
                # Split by ``` and get the middle section
                parts = cleaned.split('```')
                if len(parts) >= 3:
                    cleaned = parts[1]
                    # Remove 'json' language identifier if present
                    if cleaned.startswith('json'):
                        cleaned = cleaned[4:].strip()

            # Parse JSON
            dialogue_data = json.loads(cleaned)

            # Validate structure
            if not self._validate_dialogue(dialogue_data):
                raise ValueError("Invalid dialogue structure")

            return dialogue_data

        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            self.logger.error(f"Response text: {response_text}")
            raise ValueError("Failed to parse dialogue response as JSON")

    def _validate_dialogue(self, data: dict) -> bool:
        """
        Validate dialogue structure.

        Args:
            data: Parsed dialogue dictionary

        Returns:
            True if valid, False otherwise
        """
        # Check for dialogue key
        if 'dialogue' not in data:
            self.logger.error("Missing 'dialogue' key")
            return False

        # Check dialogue is a list
        if not isinstance(data['dialogue'], list):
            self.logger.error("'dialogue' must be a list")
            return False

        # Check minimum length
        if len(data['dialogue']) < 4:
            self.logger.error("Dialogue must have at least 4 exchanges")
            return False

        # Validate each dialogue item
        required_keys = ['speaker', 'text', 'pause_after']
        for i, item in enumerate(data['dialogue']):
            # Check all required keys present
            if not all(key in item for key in required_keys):
                self.logger.error(f"Item {i} missing required keys")
                return False

            # Check speaker is valid
            if item['speaker'] not in ['dispatcher', 'caller']:
                self.logger.error(f"Item {i} has invalid speaker: {item['speaker']}")
                return False

            # Check text is non-empty
            if not item['text'] or not item['text'].strip():
                self.logger.error(f"Item {i} has empty text")
                return False

            # Check pause_after is a number
            if not isinstance(item['pause_after'], (int, float)):
                self.logger.error(f"Item {i} has invalid pause_after type")
                return False

        return True
