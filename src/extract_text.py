import logging
from collections import Counter
from typing import Optional

from pdfixsdk import GetPdfix, PdfDoc, Pdfix

from exceptions import (
    PdfixFailedToOpenException,
    PdfixInitializeException,
)
from lang_detect import DetectLanguage
from logger import get_logger
from utils import detect_language

logger: logging.Logger = get_logger("app_logger")


class ExtractText(DetectLanguage):
    def extract_text(self) -> None:
        """
        Extract text from an input, that can be a PDF document, a TXT file or a string.
        Save the extracted text to text output file.
        """
        language: str = ""
        if self.input_path.lower().endswith(".pdf"):
            language = self._detect_language_from_pdf()
        elif self.input_path.lower().endswith(".txt"):
            language = self._detect_language_from_txt()
        else:
            logger.info(f"Input: '{self.input_path}' is not a PDF or TXT file. Detecting language from input string.")
            language = self._detect_language_from_input()

        with open(self.output_path, "w", encoding="utf-8") as outfile:
            outfile.write(language)

    def _detect_language_from_pdf(self) -> str:
        """
        Detect language from a PDF document content.

        Returns:
            The detected language.
        """
        language: str = ""
        pdfix: Optional[Pdfix] = GetPdfix()
        if pdfix is None:
            raise PdfixInitializeException()

        doc: Optional[PdfDoc] = pdfix.OpenDoc(self.input_path, "")
        if doc is None:
            raise PdfixFailedToOpenException(pdfix, self.input_path)

        try:
            # Gather words from each page
            pages_words: list[list[str]] = self._gather_words_from_each_page(pdfix, doc)
            pages: list[str] = [" ".join(page) for page in pages_words]

            # Detect languages
            languages: list[str] = []
            for page_text in pages:
                page_language: str = detect_language(page_text)
                if page_language:
                    languages.append(page_language)

            # Pick most used language
            language_counter: Counter[str] = Counter[str](languages)
            most_used_langugage: list[tuple[str, int]] = language_counter.most_common(1)
            detected_language: str = most_used_langugage[0][0] if most_used_langugage else ""

            if detected_language:
                logger.info(f"Detected language: {detected_language}")

            # Save to txt file
            language = detected_language
        except Exception:
            raise
        finally:
            doc.Close()
        pdfix.Destroy()

        return language

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
