import logging
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from pdfixsdk import (
    GetPdfix,
    PdfDoc,
    Pdfix,
    PdfPage,
    PdfTemplateQuery,
    PdsContent,
    PdsContentMark,
    PdsDictionary,
    PdsPageObject,
    PdsText,
    PsFileStream,
    kDataFormatJson,
    kEnumForms,
    kEnumResultContinue,
    kPdsPageForm,
    kPdsPageImage,
    kPdsPagePath,
    kPdsPageShading,
    kPdsPageText,
    kPsReadOnly,
    kSaveFull,
)

from exceptions import (
    PdfixFailedToLoadTemplateException,
    PdfixFailedToOpenException,
    PdfixFailedToSaveException,
    PdfixInitializeException,
)
from logger import get_logger
from set_language import SetLanguage
from utils import detect_language, max_words
from utils_sdk import (
    PageObjectEnumProcType,
    authorize_sdk,
    ensure_enum_page_objects_argtypes,
    get_pdfix_lib,
)

logger: logging.Logger = get_logger("app_logger")

_OBJECT_TYPE_NAMES = {
    kPdsPageText: "text",
    kPdsPagePath: "path",
    kPdsPageImage: "image",
    kPdsPageShading: "shading",
    kPdsPageForm: "form",
}


def _format_page_object_info(page_object: PdsPageObject) -> str:
    obj_type = _OBJECT_TYPE_NAMES.get(page_object.GetObjectType(), "unknown")
    page: Optional[PdfPage] = page_object.GetPage()
    if page is None:
        return f"type={obj_type}, page=unknown"
    return f"type={obj_type}, page={page.GetNumber()}"


def _find_lang_tag_dict(content_mark: PdsContentMark) -> Optional[PdsDictionary]:
    num_tags = content_mark.GetNumTags()
    for tag_index in range(num_tags - 1, -1, -1):
        tag_dict = content_mark.GetTagObject(tag_index)
        if tag_dict is not None and tag_dict.Known("Lang"):
            return tag_dict
    return None


def _get_last_tag_dict(content_mark: PdsContentMark) -> Optional[PdsDictionary]:
    num_tags = content_mark.GetNumTags()
    if num_tags == 0:
        return None
    return content_mark.GetTagObject(num_tags - 1)


def _get_page_object_text(page_object: PdsPageObject) -> str:
    pds_text: Optional[PdsText] = page_object.AsPdsText()
    if pds_text is None:
        return ""
    return pds_text.GetText()


@dataclass
class _PageContentEnumContext:
    doc: PdfDoc
    template_query: PdfTemplateQuery
    overwrite: bool
    maxwords: int
    default_language: str

    def enum_proc(self, page_object_ptr: int, _index: int, _client_data: int) -> int:
        page_object = PdsPageObject(page_object_ptr)
        element_info = _format_page_object_info(page_object)

        if not self.template_query.TestPageObject(page_object):
            logger.info("Template test: discarded (%s)", element_info)
            return kEnumResultContinue

        logger.info("Template test: chosen (%s)", element_info)
        self._apply_language(page_object, element_info)
        return kEnumResultContinue

    def _apply_language(self, page_object: PdsPageObject, element_info: str) -> None:
        content_mark: Optional[PdsContentMark] = page_object.GetContentMark()
        if content_mark is None:
            logger.debug("Skipping page object without content marks: %s", element_info)
            return

        lang_dict = _find_lang_tag_dict(content_mark)
        if lang_dict is not None and not self.overwrite:
            present_language = lang_dict.GetText("Lang")
            logger.debug(
                "Skipping page object with existing language (%s): %s",
                present_language,
                element_info,
            )
            return

        text = _get_page_object_text(page_object)
        if not text:
            logger.error("Failed to get text for page object: %s", element_info)
            return

        language = detect_language(max_words(text, self.maxwords))
        if not language:
            logger.warning(
                "Failed to detect language for text, using default (%s): %s",
                self.default_language,
                text,
            )
            language = self.default_language

        if lang_dict is not None:
            lang_dict.PutString("Lang", language)
            return

        last_tag_dict = _get_last_tag_dict(content_mark)
        if last_tag_dict is not None:
            last_tag_dict.PutString("Lang", language)
            return

        span_dict: Optional[PdsDictionary] = self.doc.CreateDictObject(False)
        if span_dict is None:
            logger.error("Failed to create dictionary for page object: %s", element_info)
            return

        span_dict.PutString("Lang", language)
        if not content_mark.AddTag("Span", span_dict, False):
            logger.error("Failed to add Span content mark for page object: %s", element_info)


class SetContentLanguage(SetLanguage):
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
        Initialize class for setting language to chosen content in a PDF document.

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

            if isinstance(self.regex_template, str):
                if not template_query.LoadFromRegex(self.regex_template):
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from regex")
            else:
                stream: Optional[PsFileStream] = pdfix.CreateFileStream(str(self.regex_template), kPsReadOnly)
                if stream is None:
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to create file stream for template")
                if not template_query.LoadFromStream(stream, kDataFormatJson):
                    raise PdfixFailedToLoadTemplateException(pdfix, "Failed to load template from stream")

            enum_context = _PageContentEnumContext(
                doc=doc,
                template_query=template_query,
                overwrite=self.overwrite,
                maxwords=self.maxwords,
                default_language=self.default_language,
            )
            ensure_enum_page_objects_argtypes()
            pdfix_lib = get_pdfix_lib()
            page_object_enum_proc = PageObjectEnumProcType(enum_context.enum_proc)

            page_count: int = doc.GetNumPages()
            for page_index in range(page_count):
                page: Optional[PdfPage] = doc.AcquirePage(page_index)
                if page is None:
                    logger.error("Failed to acquire page %s", page_index + 1)
                    continue

                try:
                    content: Optional[PdsContent] = page.GetContent()
                    if content is None:
                        logger.error("Failed to acquire content for page %s", page_index + 1)
                        continue

                    pdfix_lib.PdfDocEnumPageObjects(
                        doc.obj,
                        content.obj,
                        None,
                        kEnumForms,
                        page_object_enum_proc,
                        None,
                    )
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
