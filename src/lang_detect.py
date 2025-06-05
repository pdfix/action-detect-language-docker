import shutil
import sys
import tempfile
from collections import Counter

from langdetect import LangDetectException, detect
from pdfixsdk import GetPdfix, PdeElement, PdePageMap, PdeText, PdfPage, kPdeText, kSaveFull

from exceptions import PdfixException
from utils_sdk import authorize_sdk


class DetectLanguage:
    def __init__(self, license_name: str, license_key: str, input: str, output_path: str) -> None:
        """
        Initialize class for tagging pdf.

        Args:
            license_name (string): Pdfix sdk license name (e-mail).
            license_key (string): Pdfix sdk license key.
            input (string): Path or text.
            output_path (string): Path.
        """
        self.license_name = license_name
        self.license_key = license_key
        self.input = input
        self.output_path = output_path

    def detect(self) -> None:
        """
        According to chosen type of input and output create list of pages where each page contains max 100 words.
        Use these pages to detect language on each of them. Output most common language.

        Allowed input and output combination:
        - pdf 2 pdf
        - pdf 2 txt
        - txt 2 txt
        - input 2 txt
        """
        self.pdfix = GetPdfix()
        if self.pdfix is None:
            raise Exception("Pdfix Initialization fail")

        # Choose input type and read words into pages
        if self.input.lower().endswith(".pdf"):
            pages = self._extract_text_from_pdf()
        elif self.input.lower().endswith(".txt"):
            pages = self._extract_text_from_txt()
        elif self.output_path.lower().endswith(".txt"):
            pages = self._extract_text_from_input()
        else:
            print("Invalid input combination. See --help for more information.", file=sys.stderr)
            sys.exit(1)

        if len(pages) == 0 or len(pages[0]):
            print("No words were extracted from input", file=sys.stderr)
            sys.exit(1)

        # Run detect on each page
        languages: list[str] = []
        for page in pages:
            language = self._detect_language_for_page(page)
            if language:
                languages.append(language)

        # Get winning language
        language_counter = Counter(languages)
        most_used_langugage: list[tuple[str, int]] = language_counter.most_common(1)

        if most_used_langugage:
            print(f"Detected language: {most_used_langugage[0][0]}")

        content_to_write = most_used_langugage[0][0] if most_used_langugage else ""

        # Choose output type and write result
        if self.input.lower().endswith(".pdf") and self.output_path.lower().endswith(".pdf"):
            self._write_to_pdf(content_to_write)
        elif self.output_path.lower().endswith(".txt"):
            self._write_to_txt(content_to_write)
        else:
            print("Invalid input combination. See --help for more information.", file=sys.stderr)
            sys.exit(1)

    def _extract_text_from_pdf(self) -> list[list[str]]:
        """
        For given PDF document extract words from each page. Take max 100 words per page.

        Returns:
            For each page list of words.
        """
        authorize_sdk(self.pdfix, self.license_name, self.license_key)

        doc = self.pdfix.OpenDoc(self.input, "")
        if doc is None:
            raise PdfixException(self.pdfix, "Unable to open pdf")

        try:
            result: list[list[str]] = []

            for page_index in range(0, doc.GetNumPages()):
                # Acquire page
                page: PdfPage = doc.AcquirePage(page_index)
                if page is None:
                    raise PdfixException(self.pdfix, "Acquire Page fail")

                try:
                    # Get the page map of the current page
                    page_map: PdePageMap = page.AcquirePageMap()
                    if page_map is None:
                        raise PdfixException(self.pdfix, "Acquire PageMap fail")
                    try:
                        if not page_map.CreateElements():
                            raise PdfixException(self.pdfix, "Acquire PageMap fail")

                        # Get page container
                        container: PdeElement = page_map.GetElement()
                        if container is None:
                            raise PdfixException(self.pdfix, "Get page element failure")

                        # Extract max 100 words from page
                        self.words: list[str] = []
                        self._extract_words(container)
                        if len(self.words) > 0:
                            result.append(self.words)
                    except Exception:
                        raise
                    finally:
                        page_map.Release
                except Exception:
                    # Give chance to other pages (no exception propagation)
                    print(f"Problem with page {page_index + 1}", file=sys.stderr)
                finally:
                    page.Release()
        except Exception:
            raise
        finally:
            doc.Close()

        return result

    def _extract_words(self, element: PdeElement) -> None:
        """
        Extract words from text elements and crawl tree recursively.

        Args:
            element (PdeElement): Element and its children to check.
        """
        # 100 words is enough for language detection stop here
        if len(self.words) > 100:
            return

        elem_type = element.GetType()

        if kPdeText == elem_type:
            text_elem = PdeText(element.obj)
            text = text_elem.GetText()
            for word in text.split():
                self.words.append(word)
        else:
            count = element.GetNumChildren()
            if count == 0:
                return

            for child_index in range(0, count):
                child = element.GetChild(child_index)
                if child is not None:
                    self._extract_words(child)

    def _extract_text_from_txt(self) -> list[list[str]]:
        """
        For given TXT file, extract max first 100 words.

        Returns:
            One page with max 100 words.
        """
        with open(self.input, "r", encoding="utf-8") as text_file:
            all_text: str = text_file.read()

        return [all_text.split()[:100]]

    def _extract_text_from_input(self) -> list[list[str]]:
        """
        For given input string, extract max first 100 words.

        Returns:
            One page with max 100 words.
        """
        return [self.input.split()[:100]]

    def _detect_language_for_page(self, page: list[str]) -> str:
        """
        Run detection on page (max 100 words).

        Args:
            page (list[str]): List of first 100 words from page.

        Returns:
            Detected language or empty string.
        """
        try:
            text = " ".join(page)
            return detect(text)
        except LangDetectException as e:
            print(e, file=sys.stderr)
            return ""

    def _write_to_pdf(self, content_to_write: str) -> None:
        """
        Write content to PDF file specified in output_path.

        Args:
            content_to_write (str): Content.
        """
        if content_to_write:
            doc = self.pdfix.OpenDoc(self.input, "")
            if doc is None:
                raise PdfixException(self.pdfix, "Unable to open pdf")

            if not doc.SetLang(content_to_write):
                raise PdfixException(self.pdfix, "Failed to set language")

            with tempfile.NamedTemporaryFile() as temp_file:
                if not doc.Save(temp_file.name, kSaveFull):
                    raise PdfixException(self.pdfix, "Failed to save PDF")

                doc.Close()

                # Copy temp file to output path
                shutil.copyfile(temp_file.name, self.output_path)
        else:
            print("No language was detected, not setting it to PDF.", file=sys.stderr)
            sys.exit(1)

    def _write_to_txt(self, content_to_write: str) -> None:
        """
        Write content to TXT file specified in output_path.

        Args:
            content_to_write (str): Content.
        """
        with open(self.output_path, "w", encoding="utf-8") as outfile:
            outfile.write(content_to_write)
