"""Input validation utilities for the 911 Call Generator."""

def validate_prompt(prompt: str, max_length: int = 500) -> tuple[bool, str]:
    """
    Validate user prompt.

    Args:
        prompt: The user input prompt
        max_length: Maximum allowed length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not prompt or not prompt.strip():
        return False, "Prompt cannot be empty"

    if len(prompt) > max_length:
        return False, f"Prompt must be {max_length} characters or less"

    return True, ""


def validate_audio_format(format: str, allowed_formats: list[str] = None) -> bool:
    """
    Validate audio format.

    Args:
        format: The audio format (e.g., 'mp3', 'wav')
        allowed_formats: List of allowed formats

    Returns:
        True if valid, False otherwise
    """
    if allowed_formats is None:
        allowed_formats = ['mp3', 'wav']

    return format.lower() in allowed_formats
