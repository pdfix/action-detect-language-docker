import logging

from exceptions import FailToDetectLangException
from logger import get_logger
from utils import detect_language, max_words

logger: logging.Logger = get_logger("app_logger")


class DetectLanguage:
    def __init__(self, input_path: str, output_path: str, maxwords: int) -> None:
        """
        Initialize class for detecting language from a TXT file.

        Args:
            input_path (string): Path to the input TXT file.
            output_path (string): Path to the output TXT file.
            maxwords (int): How many words are considered for language detection.
        """
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.maxwords: int = maxwords

    def detect_language(self) -> None:
        """
        Detect language from the TXT file and save the language code to the output TXT file.
        """
        with open(self.input_path, "r", encoding="utf-8") as text_file:
            all_text: str = text_file.read()

        # @KA:action pdfix_detect_txt_language_to_text_langdetect
        # @KA:logic How the text file is detected
        # @KA:desc The first **Max Words** words of the whole file are detected together and only the
        # language code is written to the output file.
        # @KA:problem "No language was detected in the text." (error 30)
        # @KA:solution The file has fewer than 3 words, contains only numbers or symbols, or **Max
        # Words** is lower than 3. No output file is created.
        language: str = detect_language(max_words(all_text, self.maxwords))
        if not language:
            raise FailToDetectLangException()

        logger.info(f"Detected language: {language}")

        with open(self.output_path, "w", encoding="utf-8") as outfile:
            outfile.write(language)
