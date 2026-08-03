import logging
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from pdfixsdk import (
    GetPdfix,
    PdfDoc,
    Pdfix,
    PdfTemplateQuery,
    PdsObject,
    PdsStructElement,
    PdsStructTree,
    PsFileStream,
    kDataFormatJson,
    kEnumNone,
    kEnumResultContinue,
    kPdsStructChildElement,
    kPsReadOnly,
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
from utils import detect_language, max_words
from utils_sdk import StructElemEnumProcType, authorize_sdk, ensure_enum_struct_tree_argtypes, get_pdfix_lib

logger: logging.Logger = get_logger("app_logger")


class SetTagLanguage(SetLanguage):
    def __init__(
        self,
        license_name: str,
        license_key: str,
        input_path: str,
        regex_template: str | Path,
        output_path: str,
        maxwords: int,
        overwrite: bool,
        default_language: str,
    ) -> None:
        """
        Initialize class for setting language to chosen tags in a PDF document.

        Args:
            license_name (str): Pdfix sdk license name (e-mail).
            license_key (str): Pdfix sdk license key.
            input_path (str): Path to the PDF document.
            regex_template (str | Path): Either regex or path to the template JSON file.
            output_path (str): Path to save the PDF document.
            maxwords (int): How many words are considered for language detection.
            overwrite (bool): Whether to overwrite already existing language.
            default_language (str): Language applied when detection fails.
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.regex_template: str | Path = regex_template
        self.output_path: str = output_path
        self.maxwords: int = maxwords
        self.overwrite: bool = overwrite
        self.default_language: str = default_language
        self._struct_tree: Optional[PdsStructTree] = None
        self._template_query: Optional[PdfTemplateQuery] = None

    def set_tag_language(self) -> None:
        """
        Set language to chosen tags in a PDF document.
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

            if isinstance(self.regex_template, str):
                if not template_query.LoadFromRegex(self.regex_template):
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from regex")
            else:
                stream: Optional[PsFileStream] = pdfix.CreateFileStream(str(self.regex_template), kPsReadOnly)
                if stream is None:
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to create file stream for template")
                if not template_query.LoadFromStream(stream, kDataFormatJson):
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from stream")

            # Enumerate struct tree
            struct_tree: Optional[PdsStructTree] = doc.GetStructTree()
            if struct_tree is None:
                raise PdfixFailedToReadException(pdfix, "Failed to acquire StructTree")

            self._struct_tree = struct_tree
            self._template_query = template_query
            try:
                ensure_enum_struct_tree_argtypes()
                pdfix_lib = get_pdfix_lib()
                struct_elem_enum_proc: StructElemEnumProcType = StructElemEnumProcType(self._enum_proc)
                pdfix_lib.PdfDocEnumStructTree(doc.obj, None, kEnumNone, struct_elem_enum_proc, None)
            finally:
                self._struct_tree = None
                self._template_query = None

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

    def _enum_proc(self, _doc_ptr: int, parent_ptr: int, index: int, _client_data: int) -> int:
        """
        Callback invoked for each struct element during struct tree enumeration.

        Args:
            _doc_ptr (int): Document pointer passed by PDFix SDK (unused).
            parent_ptr (int): Parent struct element pointer, or 0 for the root.
            index (int): Child index under the parent.
            _client_data (int): Client data pointer passed by PDFix SDK (unused).

        Returns:
            Enumeration result code; always continues to the next element.
        """
        struct_element: Optional[PdsStructElement] = self._resolve_struct_element(
            self._struct_tree, parent_ptr, index
        )
        if struct_element is None:
            return kEnumResultContinue

        element_info: str = self._format_struct_element_info(struct_element)

        if self._template_query.TestStructElement(struct_element):
            logger.info("Template test: chosen (%s)", element_info)
            self._apply_language(struct_element, element_info)
        else:
            logger.info("Template test: discarded (%s)", element_info)

        return kEnumResultContinue

    def _apply_language(self, struct_element: PdsStructElement, element_info: str) -> None:
        """
        Detect language from struct element text and write it to the Lang attribute.

        Args:
            struct_element (PdsStructElement): Struct element to update.
            element_info (str): Human-readable element description for logging.
        """
        present_language: str = struct_element.GetLang()
        if present_language and not self.overwrite:
            logger.debug("Skipping element with existing language (%s): %s", present_language, element_info)
            return

        text: str = struct_element.GetActualText()
        if not text:
            text = struct_element.GetText(65535)

        if not text:
            logger.error("Failed to get text for struct element: %s", element_info)
            return

        language: str = detect_language(max_words(text, self.maxwords))
        if not language:
            logger.warning(
                "Failed to detect language for text, using default (%s): %s",
                self.default_language,
                text,
            )
            language = self.default_language

        struct_element.SetLang(language)

    def _format_struct_element_info(self, struct_element: PdsStructElement) -> str:
        """
        Build a short log-friendly description of a struct element.

        Args:
            struct_element (PdsStructElement): Struct element to describe.

        Returns:
            String with element type and page number(s).
        """
        elem_type: str = struct_element.GetType(False)
        num_pages: int = struct_element.GetNumPages()
        if num_pages == 0:
            return f"type={elem_type}, page=none"
        if num_pages == 1:
            return f"type={elem_type}, page={struct_element.GetPageNumber(0)}"
        page_nums: str = ",".join(str(struct_element.GetPageNumber(i)) for i in range(num_pages))
        return f"type={elem_type}, pages={page_nums}"

    def _resolve_struct_element(
        self, struct_tree: PdsStructTree, parent_ptr: int, index: int
    ) -> Optional[PdsStructElement]:
        """
        Resolve a struct element from enumeration parent pointer and child index.

        Args:
            struct_tree (PdsStructTree): Document struct tree.
            parent_ptr (int): Parent struct element pointer, or 0 for the root.
            index (int): Child index under the parent.

        Returns:
            Resolved struct element, or None if the child is not a struct element.
        """
        parent: PdsStructElement
        if parent_ptr:
            parent = PdsStructElement(parent_ptr)
        else:
            root_object: Optional[PdsObject] = struct_tree.GetObject()
            if root_object is None:
                return None
            root_element: Optional[PdsStructElement] = struct_tree.GetStructElementFromObject(root_object)
            if root_element is None:
                return None
            parent = root_element

        if parent.GetChildType(index) != kPdsStructChildElement:
            return None

        child_object: Optional[PdsObject] = parent.GetChildObject(index)
        if child_object is None:
            return None

        return struct_tree.GetStructElementFromObject(child_object)
