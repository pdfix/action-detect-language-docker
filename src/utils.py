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
