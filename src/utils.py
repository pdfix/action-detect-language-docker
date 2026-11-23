import logging

from langdetect import DetectorFactory, LangDetectException, detect_langs

from constants import DETECTION_MIN_PROBABILITY, DETECTION_MIN_WORDS, FALLBACK_LANGUAGE
from logger import get_logger

logger: logging.Logger = get_logger("app_logger")

# Fixed seed makes detection results repeatable for the same text
DetectorFactory.seed = 0


def detect_language(text: str) -> str:
    """
    Run detection on text. Short texts and uncertain results are not trusted.

    Args:
        text (str): Text to detect language for.

    Returns:
        Detected language or empty string when detection is not reliable.
    """
    if len(text.split()) < DETECTION_MIN_WORDS:
        return ""

    try:
        best = detect_langs(text)[0]
    except LangDetectException:
        # Text without letters (numbers, symbols)
        return ""

    if best.prob < DETECTION_MIN_PROBABILITY:
        return ""

    return best.lang


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


def resolve_default_language(user_language: str, document_language: str) -> str:
    """
    Pick language for texts where detection is not reliable.

    Args:
        user_language (str): Default language from the user, can be empty.
        document_language (str): Language of the PDF document, can be empty.

    Returns:
        User language, else document language, else fallback language.
    """
    return user_language or document_language or FALLBACK_LANGUAGE
