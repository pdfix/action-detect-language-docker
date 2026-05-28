import logging
from abc import ABC
from typing import Optional

from pdfixsdk import PdeElement, PdePageMap, PdeText, PdfDoc, Pdfix, PdfPage, kPdeText

from exceptions import (
    PdfixFailedToReadException,
)
from logger import get_logger

logger: logging.Logger = get_logger("app_logger")


class DetectLanguage(ABC):
    def __init__(self, input_path: str, output_path: str) -> None:
        """
        Initialize class for detecting language from a PDF document.

        Args:
            input_path (string): Path to the PDF document.
            output_path (string): Path to save the detected language.
        """
        self.input_path: str = input_path
        self.output_path: str = output_path

    def _gather_words_from_each_page(self, pdfix: Pdfix, doc: PdfDoc) -> list[list[str]]:
        """
        Gather words from each page of the document.

        Args:
            pdfix (Pdfix): The PDFix instance.
            doc (PdfDoc): The document to gather words from.

        Returns:
            A list of lists of words from each page.
        """
        result: list[list[str]] = []

        page_count: int = doc.GetNumPages()
        exception_for_later: Optional[Exception] = None

        for page_index in range(0, page_count):
            # Acquire page
            page: Optional[PdfPage] = doc.AcquirePage(page_index)
            if page is None:
                raise PdfixFailedToReadException(pdfix, "Failed to acquire Page")

            try:
                # Get the page map of the current page
                page_map: Optional[PdePageMap] = page.AcquirePageMap()
                if page_map is None:
                    raise PdfixFailedToReadException(pdfix, "Failed to acquire PageMap")

                try:
                    if not page_map.CreateElements():
                        raise PdfixFailedToReadException(pdfix, "Failed to create element")

                    # Get page container
                    container: Optional[PdeElement] = page_map.GetElement()
                    if container is None:
                        raise PdfixFailedToReadException(pdfix, "Failed to get page element")

                    # Extract max 100 words from page
                    words: list[str] = self._extract_words(container)
                    if len(words) > 0:
                        result.append(words[:100])

                except Exception:
                    raise
                finally:
                    page_map.Release
            except Exception as e:
                exception_for_later = e
                logger.error(f"Problem with page {page_index + 1}")
                # Give chance to other pages (no exception propagation)
            finally:
                page.Release()

        if len(result) == 0 and exception_for_later:
            raise exception_for_later

        return result

    def _extract_words(self, element: PdeElement) -> list[str]:
        """
        Extract words from text elements and crawl tree recursively.

        Args:
            element (PdeElement): Element and its children to check.

        Returns:
            List of words under element or its children.
        """
        elem_type: int = element.GetType()

        words: list[str] = []

        if kPdeText == elem_type:
            text_elem: PdeText = PdeText(element.obj)
            text: str = text_elem.GetText()
            for word in text.split():
                words.append(word)
        else:
            count: int = element.GetNumChildren()
            if count > 0:
                for child_index in range(0, count):
                    child: Optional[PdeElement] = element.GetChild(child_index)
                    if child is not None:
                        words.extend(self._extract_words(child))

        return words
