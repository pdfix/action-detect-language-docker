import logging
import shutil
import tempfile
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
from utils_sdk import authorize_sdk

logger: logging.Logger = get_logger("app_logger")


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

            if not template_query.LoadFromStream(stream, kDataFormatJson):
                raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from stream")

            # Process struct tree
            struct_tree: Optional[PdsStructTree] = doc.GetStructTree()
            if struct_tree is None:
                raise PdfixFailedToReadException(pdfix, "Failed to acquire StructTree")

            for i in range(struct_tree.GetNumChildren()):
                child_object: Optional[PdsObject] = struct_tree.GetChildObject(i)
                if child_object is None:
                    continue

                child_element: Optional[PdsStructElement] = struct_tree.GetStructElementFromObject(child_object)
                if child_element is None:
                    continue

                self._process_struct_element(template_query, struct_tree, child_element)

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

    def _process_struct_element(
        self, template_query: PdfTemplateQuery, struct_tree: PdsStructTree, struct_element: PdsStructElement
    ) -> None:

        # Check filter
        if template_query.TestStructElement(struct_element):
            # Check overwrite
            present_language: str = struct_element.GetLang()

            if present_language == "" or self.overwrite:
                # Get text
                text: str = struct_element.GetActualText()
                if not text:
                    text = struct_element.GetText(65535)

                if text:
                    language = detect_language(max_words(text, self.maxwords))
                    if language:
                        struct_element.SetLang(language)
                    else:
                        logger.error(f"Failed to detect language for text: {text}")
                else:
                    logger.error(f"Failed to get text for struct element: {struct_element}")

        # Process children
        num_kids = struct_element.GetNumChildren()

        for i in range(num_kids):
            child_object: Optional[PdsObject] = struct_element.GetChildObject(i)
            if child_object is None:
                continue

            child_element: Optional[PdsStructElement] = struct_tree.GetStructElementFromObject(child_object)
            if child_element is None:
                continue

            self._process_struct_element(template_query, struct_tree, child_element)
