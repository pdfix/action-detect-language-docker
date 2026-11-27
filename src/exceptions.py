from pdfixsdk import Pdfix

EC_ARG_GENERAL: int = 10
EC_ARG_INVALID_REGEX_OR_TEMPLATE: int = 11
EC_ARG_PARAMS: int = 12
EC_ARG_OUTPUT_FOLDER_NOT_EXISTS: int = 13
EC_ARG_INPUT_NOT_TXT: int = 14
EC_ARG_OUTPUT_EXTENSION: int = 15
EC_ARG_INPUT_NOT_PDF: int = 16

EC_PDFIX_INITIALIZE: int = 20
EC_PDFIX_ACTIVATION_FAILED: int = 21
EC_PDFIX_AUTHORIZATION_FAILED: int = 22
EC_PDFIX_FAILED_TO_READ: int = 23
EC_PDFIX_FAILED_TO_OPEN: int = 24
EC_PDFIX_FAILED_TO_SAVE: int = 25
EC_PDFIX_FAILED_TO_SAVE_LANG: int = 26
EC_PDFIX_FAILED_TO_LOAD_TEMPLATE: int = 27
EC_PDF_NOT_TAGGED: int = 28

EC_FAILED_TO_DETECT_LANG: int = 30
EC_PDF_PASSWORD: int = 31

MESSAGE_ARG_GENERAL: str = "Failed to parse arguments. Please check the usage and try again."
MESSAGE_ARG_INVALID_REGEX_OR_TEMPLATE: str = "Invalid regex or template. Please check the usage and try again."
MESSAGE_ARG_PARAMS: str = "Missing or invalid parameters."
MESSAGE_ARG_OUTPUT_FOLDER_NOT_EXISTS: str = "Output folder does not exist."
MESSAGE_ARG_INPUT_NOT_TXT: str = "Input file must be an existing TXT file."
MESSAGE_ARG_OUTPUT_NOT_PDF: str = "Output file must be PDF document."
MESSAGE_ARG_OUTPUT_NOT_TXT: str = "Output file must be TXT file."
MESSAGE_ARG_INPUT_NOT_PDF: str = "Input file must be an existing PDF document."

MESSAGE_PDFIX_INITIALIZE: str = "Failed to initialize PDFix SDK."
MESSAGE_PDFIX_ACTIVATION_FAILED: str = "Failed to activate PDFix SDK account."
MESSAGE_PDFIX_AUTHORIZATION_FAILED: str = "Failed to authorize PDFix SDK account."
MESSAGE_PDFIX_FAILED_TO_READ: str = "Failed to read PDF document."
MESSAGE_PDFIX_FAILED_TO_OPEN: str = "Failed to open PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE: str = "Failed to save PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE_LANG: str = "Failed to set language to PDF document."
MESSAGE_PDFIX_FAILED_TO_LOAD_TEMPLATE: str = "Failed to load template file."
MESSAGE_PDF_NOT_TAGGED: str = "PDF document has no tags."

MESSAGE_FAILED_TO_DETECT_LANG: str = "No language was detected in the text."
MESSAGE_PDF_PASSWORD: str = "PDF document is password-protected. Remove the password with another action first."


class ExpectedException(BaseException):
    def __init__(self, error_code: int) -> None:
        self.error_code: int = error_code
        self.message: str = ""
        # Error text from PDFix SDK, logged on its own line after the message
        self.sdk_error: str = ""

    def _add_note(self, note: str) -> None:
        self.message = note


class ArgumentException(ExpectedException):
    def __init__(self, message: str = MESSAGE_ARG_GENERAL, error_code: int = EC_ARG_GENERAL) -> None:
        super().__init__(error_code)
        self._add_note(message)


class InvalidRegexOrTemplateException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_INVALID_REGEX_OR_TEMPLATE, EC_ARG_INVALID_REGEX_OR_TEMPLATE)


class ArgumentParamsException(ArgumentException):
    def __init__(self, detail: str) -> None:
        super().__init__(f"{MESSAGE_ARG_PARAMS} {detail}", EC_ARG_PARAMS)


class ArgumentOutputFolderNotExistsException(ArgumentException):
    def __init__(self, path: str) -> None:
        super().__init__(f"{MESSAGE_ARG_OUTPUT_FOLDER_NOT_EXISTS} {path}", EC_ARG_OUTPUT_FOLDER_NOT_EXISTS)


class ArgumentInputNotTxtException(ArgumentException):
    def __init__(self, path: str) -> None:
        super().__init__(f"{MESSAGE_ARG_INPUT_NOT_TXT} {path}", EC_ARG_INPUT_NOT_TXT)


class ArgumentInputNotPdfException(ArgumentException):
    def __init__(self, path: str) -> None:
        super().__init__(f"{MESSAGE_ARG_INPUT_NOT_PDF} {path}", EC_ARG_INPUT_NOT_PDF)


class ArgumentOutputExtensionException(ArgumentException):
    def __init__(self, extension: str) -> None:
        message: str = MESSAGE_ARG_OUTPUT_NOT_PDF if extension == ".pdf" else MESSAGE_ARG_OUTPUT_NOT_TXT
        super().__init__(message, EC_ARG_OUTPUT_EXTENSION)


class PdfixInitializeException(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_PDFIX_INITIALIZE)
        self._add_note(MESSAGE_PDFIX_INITIALIZE)


class PdfixException(ExpectedException):
    def __init__(self, pdfix: Pdfix, error_code: int, message: str = "") -> None:
        super().__init__(error_code)
        self._add_note(message.strip())
        pdfix_error_code: int = pdfix.GetErrorType()
        # PDFix SDK returns error text as bytes
        pdfix_error: bytes | str = pdfix.GetError()
        pdfix_error_text: str = (
            pdfix_error.decode("utf-8", errors="replace") if isinstance(pdfix_error, bytes) else str(pdfix_error)
        )
        self.sdk_error = f"PDFix SDK error {pdfix_error_code}: {pdfix_error_text}"


class PdfixActivationException(PdfixException):
    def __init__(self, pdfix: Pdfix) -> None:
        super().__init__(pdfix, EC_PDFIX_ACTIVATION_FAILED, MESSAGE_PDFIX_ACTIVATION_FAILED)


class PdfixAuthorizationException(PdfixException):
    def __init__(self, pdfix: Pdfix) -> None:
        super().__init__(pdfix, EC_PDFIX_AUTHORIZATION_FAILED, MESSAGE_PDFIX_AUTHORIZATION_FAILED)


class PdfixFailedToReadException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, EC_PDFIX_FAILED_TO_READ, f"{MESSAGE_PDFIX_FAILED_TO_READ} {message}")


class PdfixFailedToOpenException(PdfixException):
    def __init__(self, pdfix: Pdfix, pdf_path: str = "") -> None:
        super().__init__(pdfix, EC_PDFIX_FAILED_TO_OPEN, f"{MESSAGE_PDFIX_FAILED_TO_OPEN} {pdf_path}")


class PdfixFailedToSaveException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, EC_PDFIX_FAILED_TO_SAVE, f"{MESSAGE_PDFIX_FAILED_TO_SAVE} {message}")


class PdfixFailedToSaveLanguageException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, EC_PDFIX_FAILED_TO_SAVE_LANG, f"{MESSAGE_PDFIX_FAILED_TO_SAVE_LANG} {message}")


class PdfixFailedToLoadTemplateException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, EC_PDFIX_FAILED_TO_LOAD_TEMPLATE, f"{MESSAGE_PDFIX_FAILED_TO_LOAD_TEMPLATE} {message}")


class DetectLanguageException(ExpectedException):
    def __init__(self, error_code: int, message: str) -> None:
        super().__init__(error_code)
        self._add_note(message)


class FailToDetectLangException(DetectLanguageException):
    def __init__(self) -> None:
        super().__init__(EC_FAILED_TO_DETECT_LANG, MESSAGE_FAILED_TO_DETECT_LANG)


class PdfNotTaggedException(DetectLanguageException):
    def __init__(self) -> None:
        super().__init__(EC_PDF_NOT_TAGGED, MESSAGE_PDF_NOT_TAGGED)


class PdfPasswordException(PdfixException):
    def __init__(self, pdfix: Pdfix, pdf_path: str = "") -> None:
        super().__init__(pdfix, EC_PDF_PASSWORD, f"{MESSAGE_PDF_PASSWORD} {pdf_path}")
