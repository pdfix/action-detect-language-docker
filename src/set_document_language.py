import logging
import shutil
import tempfile
from collections import Counter
from typing import Optional

from pdfixsdk import GetPdfix, PdfDoc, Pdfix, kSaveFull

from exceptions import (
    FailToDetectLangException,
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
    def __init__(
        self, license_name: str, license_key: str, input_path: str, output_path: str, maxwords: int, overwrite: bool
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
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.output_path: str = output_path
        self.maxwords: int = maxwords
        self.overwrite: bool = overwrite

    def set_document_language(self) -> None:
        """
        Set language to document metadata on a PDF document.
        """
        pdfix: Optional[Pdfix] = GetPdfix()
        if pdfix is None:
            raise PdfixInitializeException()

        authorize_sdk(pdfix, self.license_name, self.license_key)

        # @KA:action pdfix_detect_pdf_language_langdetect pdfix_detect_tag_language_to_pdf_langdetect
        # pdfix_detect_content_language_to_pdf_langdetect
        # @KA:param input_pdf
        # @KA:desc PDF document to process. It is only read, never changed.
        # @KA:problem "Failed to open PDF document." and the next log line shows "PDFix SDK error 5" (error 24)
        # @KA:solution The input file does not exist. Select the file again.
        # @KA:problem "Failed to open PDF document." and the next log line shows "PDFix SDK error 30" (error 24)
        # @KA:solution The file is not a valid PDF. Open and save it again in a PDF editor and run the
        # action again.
        # @KA:problem "Failed to open PDF document." and the next log line shows "PDFix SDK error 34" (error 24)
        # @KA:solution The PDF is password-protected. Remove the password and run the action again.
        doc: Optional[PdfDoc] = pdfix.OpenDoc(self.input_path, "")
        if doc is None:
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
        # @KA:action pdfix_detect_pdf_language_langdetect
        # @KA:logic How the document language is chosen
        # @KA:desc The first **Max Words** words of every page are detected separately. Pages with too
        # little text for a reliable result are left out, and the language found on most of the other
        # pages becomes the document language.
        # @KA:problem "No language was detected in the text." (error 30)
        # @KA:solution No page has enough text for a reliable detection (at least 3 words). The PDF may
        # be a scan without a text layer (run OCR first), contain only numbers, or **Max Words** is
        # lower than 3. No output PDF is created.
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
