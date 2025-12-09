"""
Localization utilities for ECG Monitor Application
Provides translation functionality for multi-language support
"""


def translate_text(text, language="en"):
    """
    Translate text to the specified language.
    
    Args:
        text (str): The text to translate
        language (str): The target language code (default: "en")
    
    Returns:
        str: The translated text (or original text if translation not available)
    """
    # For now, return the text as-is (no-op translation)
    # This can be extended later with actual translation dictionaries
    return text


def set_language(language="en"):
    """
    Set the application language.
    
    Args:
        language (str): The language code to set (default: "en")
    """
    # Placeholder for future language switching functionality
    pass


def get_available_languages():
    """
    Get list of available languages.
    
    Returns:
        list: List of language codes
    """
    return ["en"]  # English only for now
