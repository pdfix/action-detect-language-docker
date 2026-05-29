import logging
import shutil
import tempfile
from collections import Counter
from typing import Optional

from pdfixsdk import GetPdfix, PdfDoc, Pdfix, kSaveFull

from exceptions import (
    PdfixFailedToOpenException,
    PdfixFailedToSaveException,
    PdfixFailedToSaveLanguageException,
    PdfixInitializeException,
)
from logger import get_logger
from set_language import SetLanguage
from utils import detect_language
from utils_sdk import authorize_sdk

logger: logging.Logger = get_logger("app_logger")


class SetDocumentLanguage(SetLanguage):
    def __init__(self, license_name: str, license_key: str, input_path: str, output_path: str) -> None:
        """
        Initialize class for setting document metadata on a PDF document.

        Args:
            license_name (string): Pdfix sdk license name (e-mail).
            license_key (string): Pdfix sdk license key.
            input_path (string): Path to the PDF document.
            output_path (string): Path to save the PDF document.
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.output_path: str = output_path

    def set_document_language(self) -> None:
        """
        Set language to document metadata on a PDF document.
        """
        pdfix: Optional[Pdfix] = GetPdfix()
        if pdfix is None:
            raise PdfixInitializeException()

        authorize_sdk(pdfix, self.license_name, self.license_key)

        doc: Optional[PdfDoc] = pdfix.OpenDoc(self.input_path, "")
        if doc is None:
            raise PdfixFailedToOpenException(pdfix, self.input_path)

        try:
            # Gather words from each page
            pages_words: list[list[str]] = self._gather_words_from_each_page(pdfix, doc)
            pages: list[str] = [" ".join(page) for page in pages_words]

            # Detect languages
            languages: list[str] = []
            for text in pages:
                language: str = detect_language(text)
                if language:
                    languages.append(language)

            # Pick most used language
            language_counter: Counter[str] = Counter[str](languages)
            most_used_langugage: list[tuple[str, int]] = language_counter.most_common(1)
            detected_language: str = most_used_langugage[0][0] if most_used_langugage else ""

            if most_used_langugage:
                logger.info(f"Detected language: {detected_language}")

            # Set language to document metadata
            if not doc.SetLang(detected_language):
                raise PdfixFailedToSaveLanguageException(pdfix)

            # Save document
            with tempfile.NamedTemporaryFile() as temp_file:
                if not doc.Save(temp_file.name, kSaveFull):
                    raise PdfixFailedToSaveException(pdfix, temp_file.name)

                # Copy temp file to output path
                shutil.copyfile(temp_file.name, self.output_path)
        except Exception:
            raise
        finally:
            doc.Close()
        pdfix.Destroy()
