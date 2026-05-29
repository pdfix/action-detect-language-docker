import logging

from logger import get_logger
from utils import detect_language

logger: logging.Logger = get_logger("app_logger")


class DetectLanguage:
    def __init__(self, input_path: str, output_path: str) -> None:
        """
        Initialize class for extracting text from an input, that can be a TXT file or a string.

        Args:
            input_path (string): Path to the input file.
            output_path (string): Path to the output TXT file.
        """
        self.input_path: str = input_path
        self.output_path: str = output_path

    def detect_language(self) -> None:
        """
        Detect language from an input, that can be a TXT file or a string.
        Save the extracted text to text output file.
        """
        language: str = ""

        if self.input_path.lower().endswith(".txt"):
            language = self._detect_language_from_txt()
        else:
            logger.info(f"Input: '{self.input_path}' is not a PDF or TXT file. Detecting language from input string.")
            language = self._detect_language_from_input()

        with open(self.output_path, "w", encoding="utf-8") as outfile:
            outfile.write(language)

    def _detect_language_from_txt(self) -> str:
        language: str = ""

        with open(self.input_path, "r", encoding="utf-8") as text_file:
            all_text: str = text_file.read()

        text: str = " ".join(all_text.split()[:100])
        language = detect_language(text)
        logger.info(f"Detected language: {language}")

        return language

    def _detect_language_from_input(self) -> str:
        language: str = ""

        text: str = " ".join(self.input_path.split()[:100])
        language = detect_language(text)
        logger.info(f"Detected language: {language}")

        return language
