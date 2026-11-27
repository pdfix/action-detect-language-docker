import logging
import shutil
import tempfile
from collections import Counter
from typing import Optional

from pdfixsdk import GetPdfix, PdfDoc, Pdfix, kSaveFull

from constants import SDK_ERROR_INVALID_PASSWORD
from exceptions import (
    FailToDetectLangException,
    PdfixFailedToOpenException,
    PdfixFailedToSaveException,
    PdfixFailedToSaveLanguageException,
    PdfixInitializeException,
    PdfPasswordException,
)
from logger import get_logger
from set_language import SetLanguage
from utils import detect_language
from utils_sdk import authorize_sdk

logger: logging.Logger = get_logger("app_logger")


class SetDocumentLanguage(SetLanguage):
    def __init__(
        self,
        license_name: str,
        license_key: str,
        input_path: str,
        output_path: str,
        maxwords: int,
        overwrite: bool,
        password: str = "",
    ) -> None:
        """
        Initialize class for setting document metadata on a PDF document.

        Args:
            license_name (string): Pdfix sdk license name (e-mail).
            license_key (string): Pdfix sdk license key.
            input_path (string): Path to the PDF document.
            output_path (string): Path to save the PDF document.
            maxwords (int): How many words are considered for language detection.
            overwrite (bool): Whether to overwrite already existing document language.
            password (str): Password of the PDF document, empty when it has none.
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.maxwords: int = maxwords
        self.overwrite: bool = overwrite
        self.password: str = password

    def set_document_language(self) -> None:
        """
        Set language to document metadata on a PDF document.
        """
        pdfix: Optional[Pdfix] = GetPdfix()
        if pdfix is None:
            raise PdfixInitializeException()

        authorize_sdk(pdfix, self.license_name, self.license_key)

        doc: Optional[PdfDoc] = pdfix.OpenDoc(self.input_path, self.password)
        if doc is None:
            if pdfix.GetErrorType() == SDK_ERROR_INVALID_PASSWORD:
                raise PdfPasswordException(pdfix, self.input_path)
            raise PdfixFailedToOpenException(pdfix, self.input_path)

        try:
            present_language: str = doc.GetLang()
            if present_language and not self.overwrite:
                logger.info(f"Document already has language {present_language}, keeping it")
            else:
                detected_language: str = self._detect_document_language(pdfix, doc)
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

    def _detect_document_language(self, pdfix: Pdfix, doc: PdfDoc) -> str:
        """
        Detect language of each page and pick the most used one.

        Args:
            pdfix (Pdfix): The PDFix instance.
            doc (PdfDoc): The document to detect language for.

        Returns:
            Detected language.
        """
        # Gather words from each page
        pages_words: list[list[str]] = self._gather_words_from_each_page(pdfix, doc, self.maxwords)
        pages: list[str] = [" ".join(page) for page in pages_words]

        # Detect languages
        languages: list[str] = []
        for text in pages:
            language: str = detect_language(text)
            if language:
                languages.append(language)

        # Pick most used language
        language_counter: Counter[str] = Counter[str](languages)
        most_used_language: list[tuple[str, int]] = language_counter.most_common(1)
        if not most_used_language:
            raise FailToDetectLangException()

        return most_used_language[0][0]
