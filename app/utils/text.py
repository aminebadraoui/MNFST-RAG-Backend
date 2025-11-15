"""
Text utility functions
"""


def clamp_text(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Clamp text to a maximum length, adding a suffix if truncated
    
    Args:
        text: The text to clamp
        max_length: Maximum length of the text (including suffix)
        suffix: Suffix to add if text is truncated
        
    Returns:
        Clamped text
    """
    if len(text) <= max_length:
        return text
    
    # Reserve space for suffix
    clamp_length = max_length - len(suffix)
    return text[:clamp_length] + suffix