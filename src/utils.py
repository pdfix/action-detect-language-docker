import logging

from langdetect import LangDetectException, detect

from logger import get_logger

logger: logging.Logger = get_logger("app_logger")


def detect_language(text: str) -> str:
    """
    Run detection on text.

    Args:
        text (str): Text to detect language for.

    Returns:
        Detected language or empty string.
    """
    try:
        return detect(text)
    except LangDetectException as e:
        logger.error(e)
        return ""


def max_words(text: str, maxwords: int) -> str:
    """
    Get max X words from text.

    Args:
        text (str): Text to get max words from.
        maxwords (int): How many words to get.

    Returns:
        Max X words from text.
    """
    return " ".join(text.split()[:maxwords])
