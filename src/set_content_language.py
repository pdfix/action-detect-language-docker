import logging
import shutil
import tempfile
from typing import Optional

from pdfixsdk import (
    GetPdfix,
    PdfDoc,
    Pdfix,
    PdfPage,
    PdfTemplateQuery,
    PdsContent,
    PdsContentMark,
    PdsForm,
    PdsObject,
    PdsPageObject,
    PdsStream,
    PdsStructElement,
    PdsStructTree,
    PdsText,
    kDataFormatJson,
    kSaveFull,
)

from exceptions import (
    PdfixFailedToLoadTemplateException,
    PdfixFailedToOpenException,
    PdfixFailedToReadException,
    PdfixFailedToSaveException,
    PdfixInitializeException,
)
from logger import get_logger
from set_language import SetLanguage
from utils import detect_language
from utils_sdk import authorize_sdk

logger: logging.Logger = get_logger("app_logger")


class SetContentLanguage(SetLanguage):
    def __init__(
        self, license_name: str, license_key: str, input_path: str, template_path: str, output_path: str
    ) -> None:
        """
        Initialize class for setting language to chosen tags in a PDF document.

        Args:
            license_name (string): Pdfix sdk license name (e-mail).
            license_key (string): Pdfix sdk license key.
            input_path (string): Path to the PDF document.
            template_path (string): Path to the template file.
            output_path (string): Path to save the PDF document.
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.template_path: str = template_path
        self.output_path: str = output_path

    def set_content_language(self) -> None:
        """
        Set language to chosen content in a PDF document.
        """
        pdfix: Optional[Pdfix] = GetPdfix()
        if pdfix is None:
            raise PdfixInitializeException()

        authorize_sdk(pdfix, self.license_name, self.license_key)

        doc: Optional[PdfDoc] = pdfix.OpenDoc(self.input_path, "")
        if doc is None:
            raise PdfixFailedToOpenException(pdfix, self.input_path)

        try:
            # Load template query
            template_query: Optional[PdfTemplateQuery] = doc.CreateTemplateQuery()
            if template_query is None:
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to create Template query")

            stream: Optional[PdsStream] = pdfix.CreateFileStream(self.template_path, "r")
            if stream is None:
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to create file stream for template")

            if not template_query.LoadFromStream(stream, kDataFormatJson):
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from stream")

            # Acquire struct tree
            struct_tree: Optional[PdsStructTree] = doc.GetStructTree()
            if struct_tree is None:
                raise PdfixFailedToReadException(pdfix, "Failed to acquire StructTree")

            # Process each page
            page_count: int = doc.GetNumPages()
            for page_index in range(page_count):
                page: Optional[PdfPage] = doc.AcquirePage(page_index)
                if page is None:
                    logger.error(f"Failed to acquire page {page_index + 1}")
                    continue

                try:
                    content: Optional[PdsContent] = page.GetContent()
                    if content is None:
                        logger.error(f"Failed to acquire content for page {page_index + 1}")
                        continue

                    self._process_content(template_query, struct_tree, content)
                finally:
                    page.Release()

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

    def _process_content(
        self, template_query: PdfTemplateQuery, struct_tree: PdsStructTree, content: PdsContent
    ) -> None:
        # Process each page object
        for object_index in range(content.GetNumObjects()):
            page_object: Optional[PdsPageObject] = content.GetObject(object_index)
            if page_object is None:
                continue

            self._process_page_object(template_query, struct_tree, page_object)

    def _process_page_object(
        self, template_query: PdfTemplateQuery, struct_tree: PdsStructTree, page_object: PdsPageObject
    ) -> None:
        content_mark: Optional[PdsContentMark] = page_object.GetContentMark()
        if content_mark is not None:
            self._process_content_marks(template_query, struct_tree, page_object, content_mark)

        if isinstance(page_object, PdsForm):
            form_content: Optional[PdsContent] = page_object.GetContent()
            if form_content is not None:
                self._process_content(template_query, struct_tree, form_content)

    def _process_content_marks(
        self,
        template_query: PdfTemplateQuery,
        struct_tree: PdsStructTree,
        page_object: PdsPageObject,
        content_mark: PdsContentMark,
    ) -> None:
        num_tags: int = content_mark.GetNumTags()
        if num_tags == 0:
            return

        text: str = self._get_page_object_text(page_object)

        for tag_index in range(num_tags - 1, -1, -1):
            struct_element: Optional[PdsStructElement] = self._get_struct_element_for_tag(
                struct_tree, page_object, content_mark, tag_index
            )
            if struct_element is None:
                continue

            # Check filter
            if not template_query.TestStructElement(struct_element):
                continue

            if not text:
                logger.error(f"Failed to get text for page object: {page_object}")
                return

            language: str = detect_language(text)
            if language:
                struct_element.SetLang(language)
            else:
                logger.error(f"Failed to detect language for text: {text}")
            return

    def _get_struct_element_for_tag(
        self,
        struct_tree: PdsStructTree,
        page_object: PdsPageObject,
        content_mark: PdsContentMark,
        tag_index: int,
    ) -> Optional[PdsStructElement]:
        tag_object: Optional[PdsObject] = content_mark.GetTagObject(tag_index)
        if tag_object is not None:
            struct_element: Optional[PdsStructElement] = struct_tree.GetStructElementFromObject(tag_object)
            if struct_element is not None:
                return struct_element

        struct_object: Optional[PdsObject] = page_object.GetStructObject(False)
        if struct_object is not None:
            return struct_tree.GetStructElementFromObject(struct_object)

        return None

    def _get_page_object_text(self, page_object: PdsPageObject) -> str:
        # Get text from page object
        if isinstance(page_object, PdsText):
            return page_object.GetText()
        return ""
