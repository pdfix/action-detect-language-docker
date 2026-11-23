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
    # @KA:action pdfix_detect_pdf_language_langdetect pdfix_detect_tag_language_to_pdf_langdetect
    # pdfix_detect_content_language_to_pdf_langdetect pdfix_detect_txt_language_to_text_langdetect
    # @KA:logic Reliable language detection
    # @KA:desc Language is detected by LangDetect, which knows 55 languages and returns the main
    # language code only, for example `en`, not `en-GB`. A result is used only when the text has at
    # least 8 words and the detection is at least 90 % certain; shorter texts are often detected as a
    # wrong language. Text made only of numbers or symbols has no language. The same text always gives
    # the same result.
    # @KA:problem Similar languages are mixed up, for example Czech and Slovak.
    # @KA:solution Closely related languages need longer text. Increase **Max Words**, or set the
    # language of such passages manually.
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
    # @KA:action pdfix_detect_tag_language_to_pdf_langdetect pdfix_detect_content_language_to_pdf_langdetect
    # @KA:param default_language
    # @KA:desc Language written to text that is too short or too uncertain for a reliable detection,
    # for example headings, table cells or numbers. When empty (default), the document language is
    # used, and `en` when the document has no language. Enter a language code such as `de` to use it
    # instead.
    # @KA:problem A short passage in another language got the document language.
    # @KA:solution The passage has fewer than 8 words, so it cannot be detected reliably. Set the
    # language of that tag manually in PDFix Desktop.
    return user_language or document_language or FALLBACK_LANGUAGE
