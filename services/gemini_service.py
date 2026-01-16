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
        dispatcher_protocol_questions: str = '',
        call_type: str = 'emergency',
        nurse_protocol_questions: str = '',
        nurse_gender: str = 'unknown',
        erratic_level: str = 'none',
        language: str = 'en',
        dispatcher_language: str = 'en',
        caller_language: str = 'en'
    ) -> dict:
        """
        Generate 911 call dialogue based on scenario.

        Args:
            scenario: Description of the emergency scenario
            target_duration: Target call duration in seconds (default: 60)
            emotion_level: Caller emotion level (calm, concerned, anxious, panicked, hysterical)
            dispatcher_gender: Gender of dispatcher voice (male, female, unknown)
            caller_gender: Gender of caller voice (male, female, unknown)
            dispatcher_protocol_questions: Optional specific questions dispatcher must ask
            call_type: Type of call - 'emergency', 'transfer', or 'warm_transfer'
            nurse_protocol_questions: Optional specific questions nurse must ask (warm_transfer only)
            nurse_gender: Gender of nurse voice (male, female, unknown)
            erratic_level: Caller erratic behavior level (none, slight, moderate, high, extreme)

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
        prompt = self._build_prompt(scenario, target_duration, emotion_level, dispatcher_gender, caller_gender, dispatcher_protocol_questions, call_type, nurse_protocol_questions, nurse_gender, erratic_level, language, dispatcher_language, caller_language)

        try:
            protocol_msg = ""
            if dispatcher_protocol_questions:
                protocol_msg += f", dispatcher protocol: {len(dispatcher_protocol_questions.splitlines())} questions"
            if nurse_protocol_questions:
                protocol_msg += f", nurse protocol: {len(nurse_protocol_questions.splitlines())} questions"

            self.logger.info(f"Generating dialogue for scenario: {scenario[:50]}... (type: {call_type}, target: {target_duration}s, emotion: {emotion_level}, dispatcher: {dispatcher_gender}, caller: {caller_gender}{protocol_msg})")
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
        dispatcher_protocol_questions: str = '',
        call_type: str = 'emergency',
        nurse_protocol_questions: str = '',
        nurse_gender: str = 'unknown',
        erratic_level: str = 'none',
        language: str = 'en',
        dispatcher_language: str = 'en',
        caller_language: str = 'en'
    ) -> str:
        """
        Build prompt for Gemini to generate realistic 911 dialogue.

        Args:
            scenario: User's emergency scenario description
            target_duration: Target duration in seconds
            emotion_level: Caller emotion level
            dispatcher_gender: Gender of dispatcher
            caller_gender: Gender of caller
            dispatcher_protocol_questions: Optional specific questions dispatcher should ask
            call_type: Type of call - 'emergency', 'transfer', or 'warm_transfer'
            nurse_protocol_questions: Optional specific questions nurse should ask
            nurse_gender: Gender of nurse
            erratic_level: Caller erratic behavior level

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

        # Map erratic level to behavior description for prompt
        erratic_descriptions = {
            'none': '',
            'slight': 'The caller occasionally goes on minor tangents or provides slightly unnecessary details, but stays mostly focused.',
            'moderate': 'The caller has some difficulty staying on topic, occasionally rambles, and may need to be redirected by the dispatcher.',
            'high': 'The caller frequently interrupts, jumps between topics, rambles significantly, and is difficult to keep focused. The dispatcher must work hard to extract necessary information.',
            'extreme': 'The caller is highly erratic and incoherent, constantly interrupting, jumping wildly between unrelated topics, providing confusing or contradictory information, making it very challenging for the dispatcher to gather critical details.'
        }
        erratic_desc = erratic_descriptions.get(erratic_level, '')
        erratic_note = f"\n\nIMPORTANT - Caller Behavior:\n{erratic_desc}" if erratic_desc else ""

        # Build gender context for the prompt
        dispatcher_desc = ""
        if dispatcher_gender in ['male', 'female']:
            dispatcher_desc = f" The dispatcher is {dispatcher_gender}."

        caller_desc = ""
        if caller_gender in ['male', 'female']:
            caller_desc = f" The caller is {caller_gender}."

        gender_context = f"{dispatcher_desc}{caller_desc}" if (dispatcher_desc or caller_desc) else ""

        # Build gender context for nurse
        nurse_desc = ""
        if nurse_gender in ['male', 'female']:
            nurse_desc = f" The nurse is {nurse_gender}."

        # Map language code to full name
        language_names = {
            'en': 'English',
            'es': 'Spanish',
            'fr': 'French',
            'de': 'German',
            'it': 'Italian',
            'pt': 'Portuguese',
            'pl': 'Polish',
            'hi': 'Hindi',
            'ja': 'Japanese',
            'ko': 'Korean',
            'zh': 'Chinese (Mandarin)',
            'ar': 'Arabic'
        }
        language_name = language_names.get(language, 'English')
        language_instruction = f"\n\nCRITICAL - Language Requirement:\nYou MUST generate ALL dialogue in {language_name}. Every line spoken by the dispatcher, caller, and nurse must be in {language_name}. Use natural, native {language_name} phrasing appropriate for emergency services." if language != 'en' else ""

        # Build protocol questions sections if provided
        dispatcher_protocol_section = ""
        if dispatcher_protocol_questions:
            dispatcher_protocol_section = f"""

IMPORTANT - Dispatcher Protocol Questions:
The dispatcher MUST ask these specific questions during their part of the call (integrate them naturally):
{dispatcher_protocol_questions}
"""

        nurse_protocol_section = ""
        if nurse_protocol_questions:
            nurse_protocol_section = f"""

IMPORTANT - Nurse Protocol Questions:
The nurse MUST ask these specific questions during the assessment (integrate them naturally):
{nurse_protocol_questions}
"""

        # Build different prompts based on call type
        if call_type == 'with_translator':
            # Translator scenario (3-speaker: dispatcher, caller, translator)
            # Map language codes to full names for the prompt
            dispatcher_language_name = language_names.get(dispatcher_language, 'English')
            caller_language_name = language_names.get(caller_language, 'Spanish')

            return f"""You are an expert in creating realistic 911 call scenarios with language barriers for training purposes.

Generate a dialogue where a 911 dispatcher communicates with a non-English speaking caller through a bilingual translator. The conversation has THREE speakers:
1. Dispatcher (speaks {dispatcher_language_name} only)
2. Translator (bilingual, facilitates communication between dispatcher and caller)
3. Caller (speaks {caller_language_name} only)

Scenario: {scenario}{dispatcher_protocol_section}{erratic_note}

CRITICAL - Language Requirements:
- The DISPATCHER must speak ONLY in {dispatcher_language_name}. Every line by the dispatcher MUST be in {dispatcher_language_name}.
- The CALLER must speak ONLY in {caller_language_name}. Every line by the caller MUST be in {caller_language_name}.
- The TRANSLATOR is bilingual and alternates between both languages:
  * When translating the dispatcher's questions to the caller, speak in {caller_language_name}
  * When translating the caller's responses to the dispatcher, speak in {dispatcher_language_name}
  * The translator should provide seamless, direct translations without prefacing them with phrases like "They're saying..." or "I'll translate..."

Requirements:
1. Start with dispatcher greeting in {dispatcher_language_name}
2. Caller responds in {caller_language_name} - language barrier is evident
3. Dispatcher recognizes the language barrier and explicitly brings in the translator as a resource (e.g., "Hold on, I'm connecting our {caller_language_name} translator" or "Let me get our language line on the call")
4. Translator joins and introduces themselves briefly in both languages
5. Dispatcher asks questions in {dispatcher_language_name} -> Translator translates to {caller_language_name} -> Caller responds in {caller_language_name} -> Translator translates back to {dispatcher_language_name}
6. Include {exchange_range} exchanges total (target duration: ~{{target_duration}} seconds)
7. Dispatcher voice: professional, calm, familiar with using translator services{dispatcher_desc}
8. Translator voice: clear, helpful, professional, switches languages fluidly{nurse_desc}
9. Caller emotion level: {emotion_desc}{caller_desc}
10. Dispatcher gathers key information through translator: location, emergency type, injuries/hazards
11. Use appropriate pronouns and references based on the gender of each speaker
12. If protocol questions are provided above, ensure the dispatcher asks them (translated through interpreter)
13. Format as JSON with this EXACT structure:

{{{{
  "dialogue": [
    {{{{"speaker": "dispatcher", "text": "Nine one one, what's your emergency?", "pause_after": 0.5}}}},
    {{{{"speaker": "caller", "text": "[Urgent response in {caller_language_name}]", "pause_after": 0.8}}}},
    {{{{"speaker": "dispatcher", "text": "[In {dispatcher_language_name}] Okay, I hear you need help. Let me connect our {caller_language_name} translator. One moment.", "pause_after": 0.6}}}},
    {{{{"speaker": "translator", "text": "[In {dispatcher_language_name}] Translator here, I can help. [Then in {caller_language_name} to caller] Hello, this is the translator.", "pause_after": 0.6}}}},
    {{{{"speaker": "dispatcher", "text": "[In {dispatcher_language_name}] Thank you. Please ask them what their emergency is and where they are.", "pause_after": 0.5}}}},
    {{{{"speaker": "translator", "text": "[In {caller_language_name} to caller] What is your emergency? Where are you located?", "pause_after": 0.7}}}},
    {{{{"speaker": "caller", "text": "[Describes emergency and location in {caller_language_name}]", "pause_after": 0.9}}}},
    {{{{"speaker": "translator", "text": "[In {dispatcher_language_name} to dispatcher] There's [emergency description]. Located at [location].", "pause_after": 0.6}}}},
    {{{{"speaker": "dispatcher", "text": "[In {dispatcher_language_name}] Got it. Ask if anyone is injured.", "pause_after": 0.5}}}}
  ],
  "metadata": {{{{
    "scenario_type": "medical/fire/police/traffic",
    "urgency_level": "low/medium/high/critical"
  }}}}
}}}}

Rules for pauses:
- Dispatcher: 0.3-0.6 seconds (professional, quick responses)
- Translator: 0.4-0.7 seconds (clear, measured)
- Caller: 0.6-1.2 seconds (emotional, varied based on emotion level)
- After questions: 0.7-1.0 seconds to allow thinking time

Important:
- Make the dialogue realistic and natural with authentic language barrier challenges
- The dispatcher should actively bring the translator into the call as a known resource/service
- Show the dispatcher's familiarity with using translator services (e.g., "Let me connect our translator", "I'm bringing in our language line")
- The translator acts as a professional language service, not just someone who happens to be available
- Translator should introduce themselves professionally in both languages when joining
- The dispatcher directs the translator on what questions to ask
- Dispatcher should gather critical 911 information through the translator: location, emergency type, injuries, immediate hazards
- Caller should sound appropriately stressed based on emotion level
- Each speaker MUST use their assigned language (no mixing except for the translator)
- Return ONLY valid JSON, no additional text or explanation"""

        elif call_type == 'warm_transfer':
            # Warm transfer to nurse (3-speaker dialogue)
            return f"""You are an expert in creating realistic 911 warm transfer scenarios for medical triage training purposes.

Generate a dialogue where a 911 dispatcher transfers a caller to a nurse for medical assessment. The conversation has THREE speakers:
1. Dispatcher (introduces situation to nurse)
2. Nurse (asks clarifying questions)
3. Caller (describes medical condition)

Scenario: {scenario}{dispatcher_protocol_section}{nurse_protocol_section}{erratic_note}{language_instruction}

Requirements:
1. Start with dispatcher explaining situation to nurse (2-3 exchanges)
2. Dispatcher brings caller into conversation: "I'm going to connect you with our nurse now"
3. Nurse takes over, asking caller medical questions (6-10 exchanges)
4. Include {exchange_range} exchanges total (target duration: ~{target_duration} seconds)
5. Dispatcher voice: professional, brief{dispatcher_desc}
6. Nurse voice: calm, professional, asks assessment questions{nurse_desc}
7. Caller emotion level: {emotion_desc}{caller_desc}
8. Nurse asks protocol questions: chief complaint, symptoms, duration, medications, allergies
9. Use appropriate pronouns and references based on the gender of each speaker
10. If dispatcher protocol questions are provided above, ensure the dispatcher asks them before transferring
11. If nurse protocol questions are provided above, ensure the nurse asks them during the assessment
12. Format as JSON with this EXACT structure:

{{
  "dialogue": [
    {{"speaker": "dispatcher", "text": "Nurse triage, I have a caller on the line", "pause_after": 0.5}},
    {{"speaker": "nurse", "text": "Go ahead, what's the situation?", "pause_after": 0.4}},
    {{"speaker": "dispatcher", "text": "Caller reporting...", "pause_after": 0.6}},
    {{"speaker": "nurse", "text": "Thank you. Please connect me with the caller", "pause_after": 0.5}},
    {{"speaker": "dispatcher", "text": "I'm connecting you now", "pause_after": 0.5}},
    {{"speaker": "nurse", "text": "Hello, this is the triage nurse. Can you tell me what's going on?", "pause_after": 0.7}},
    {{"speaker": "caller", "text": "I'm having...", "pause_after": 0.8}},
    {{"speaker": "nurse", "text": "How long have you been experiencing this?", "pause_after": 0.6}}
  ],
  "metadata": {{
    "scenario_type": "medical",
    "urgency_level": "low/medium/high/critical"
  }}
}}

Rules for pauses:
- Dispatcher: 0.3-0.6 seconds (quick, professional)
- Nurse: 0.4-0.7 seconds (calm, measured)
- Caller: 0.6-1.2 seconds (emotional, varied based on urgency)
- After questions: 0.7-1.0 seconds to allow thinking time

Important:
- Make the dialogue realistic and natural
- Nurse should gather: chief complaint, onset, severity, associated symptoms, medical history
- Caller should sound appropriately concerned based on emotion level
- Return ONLY valid JSON, no additional text or explanation"""

        elif call_type == 'transfer':
            # Dispatcher-to-dispatcher transfer
            return f"""You are an expert in creating realistic 911 dispatcher-to-dispatcher transfer scenarios for training purposes.

Generate a dialogue where one dispatcher is transferring a call/incident to another dispatcher (or supervisor/specialist) based on this scenario:
{scenario}{dispatcher_protocol_section}{language_instruction}

Requirements:
1. Speaker 1 (transferring dispatcher) should be professional and provide key information{dispatcher_desc}
2. Speaker 2 (receiving dispatcher) should ask clarifying questions and confirm details{caller_desc}
3. Include {exchange_range} exchanges total (target duration: ~{target_duration} seconds)
4. Transferring dispatcher shares: incident type, location, current status, units on scene, special concerns
5. Receiving dispatcher confirms understanding and may ask for additional details
6. Both speakers should use professional radio/dispatch terminology
7. Use appropriate pronouns and references based on the gender of each speaker
8. If protocol questions are provided above, ensure they are asked naturally within the conversation
9. Format as JSON with this EXACT structure:

{{
  "dialogue": [
    {{"speaker": "dispatcher", "text": "Dispatch 4 to Dispatch 7, transferring a call", "pause_after": 0.5}},
    {{"speaker": "caller", "text": "Go ahead Dispatch 4", "pause_after": 0.4}},
    {{"speaker": "dispatcher", "text": "I have a code 3 incident at...", "pause_after": 0.6}}
  ],
  "metadata": {{
    "scenario_type": "medical/fire/police/traffic/other",
    "urgency_level": "low/medium/high/critical"
  }}
}}

Rules for pauses:
- Both dispatchers use short, professional pauses: 0.3-0.6 seconds
- After questions: 0.5-0.8 seconds to allow response time

Important:
- Make the dialogue realistic and professional
- Include relevant incident details
- Both speakers should use dispatch terminology and codes where appropriate
- Return ONLY valid JSON, no additional text or explanation"""

        else:
            # Emergency call (dispatcher to caller)
            return f"""You are an expert in creating realistic 911 emergency call scenarios for training purposes.

Generate a dialogue between a 911 dispatcher and a caller based on this scenario:
{scenario}{dispatcher_protocol_section}{erratic_note}{language_instruction}

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
            if item['speaker'] not in ['dispatcher', 'caller', 'nurse', 'translator']:
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
