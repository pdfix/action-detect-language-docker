import logging
import shutil
import tempfile
from dataclasses import dataclass
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


def _format_struct_element_info(struct_element: PdsStructElement) -> str:
    elem_type = struct_element.GetType(False)
    num_pages = struct_element.GetNumPages()
    if num_pages == 0:
        return f"type={elem_type}, page=none"
    if num_pages == 1:
        return f"type={elem_type}, page={struct_element.GetPageNumber(0)}"
    page_nums = ",".join(str(struct_element.GetPageNumber(i)) for i in range(num_pages))
    return f"type={elem_type}, pages={page_nums}"


def _resolve_struct_element(struct_tree: PdsStructTree, parent_ptr: int, index: int) -> Optional[PdsStructElement]:
    if parent_ptr:
        parent = PdsStructElement(parent_ptr)
    else:
        root_object = struct_tree.GetObject()
        if root_object is None:
            return None
        parent = struct_tree.GetStructElementFromObject(root_object)
        if parent is None:
            return None

    if parent.GetChildType(index) != kPdsStructChildElement:
        return None

    child_object: Optional[PdsObject] = parent.GetChildObject(index)
    if child_object is None:
        return None

    return struct_tree.GetStructElementFromObject(child_object)


@dataclass
class _StructTreeEnumContext:
    struct_tree: PdsStructTree
    template_query: PdfTemplateQuery
    overwrite: bool
    maxwords: int

    def enum_proc(self, _doc_ptr: int, parent_ptr: int, index: int, _client_data: int) -> int:
        struct_element = _resolve_struct_element(self.struct_tree, parent_ptr, index)
        if struct_element is None:
            return kEnumResultContinue

        element_info = _format_struct_element_info(struct_element)

        if self.template_query.TestStructElement(struct_element):
            logger.info("Template test: chosen (%s)", element_info)
            self._apply_language(struct_element, element_info)
        else:
            logger.info("Template test: discarded (%s)", element_info)

        return kEnumResultContinue

    def _apply_language(self, struct_element: PdsStructElement, element_info: str) -> None:
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

        language = detect_language(max_words(text, self.maxwords))
        if language:
            struct_element.SetLang(language)
        else:
            logger.error("Failed to detect language for text: %s", text)


class SetTagLanguage(SetLanguage):
    def __init__(
        self,
        license_name: str,
        license_key: str,
        input_path: str,
        template_path: str,
        output_path: str,
        maxwords: int,
        overwrite: bool,
    ) -> None:
        """
        Initialize class for setting language to chosen tags in a PDF document.

        Args:
            license_name (string): Pdfix sdk license name (e-mail).
            license_key (string): Pdfix sdk license key.
            input_path (string): Path to the PDF document.
            template_path (string): Path to the template file.
            output_path (string): Path to save the PDF document.
            maxwords (int): How many words are considered for language detection.
            overwrite (bool): Whether to overwrite already existing language.
        """
        self.license_name: str = license_name
        self.license_key: str = license_key
        self.input_path: str = input_path
        self.template_path: str = template_path
        self.output_path: str = output_path
        self.maxwords: int = maxwords
        self.overwrite: bool = overwrite

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

            stream: Optional[PsFileStream] = pdfix.CreateFileStream(self.template_path, kPsReadOnly)
            if stream is None:
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to create file stream for template")

            # TODO load regex using: template_query.LoadFromRegex(pattern)

            if not template_query.LoadFromStream(stream, kDataFormatJson):
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from stream")

            # Enumerate struct tree
            struct_tree: Optional[PdsStructTree] = doc.GetStructTree()
            if struct_tree is None:
                raise PdfixFailedToReadException(pdfix, "Failed to acquire StructTree")

            enum_context = _StructTreeEnumContext(
                struct_tree=struct_tree,
                template_query=template_query,
                overwrite=self.overwrite,
                maxwords=self.maxwords,
            )
            ensure_enum_struct_tree_argtypes()
            pdfix_lib = get_pdfix_lib()
            struct_elem_enum_proc = StructElemEnumProcType(enum_context.enum_proc)
            pdfix_lib.PdfDocEnumStructTree(doc.obj, None, kEnumNone, struct_elem_enum_proc, None)

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
