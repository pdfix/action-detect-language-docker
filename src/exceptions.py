from pdfixsdk import Pdfix

EC_ARG_GENERAL: int = 10
EC_ARG_INVALID_REGEX_OR_TEMPLATE: int = 11

EC_PDFIX_INITIALIZE: int = 20
EC_PDFIX_ACTIVATION_FAILED: int = 21
EC_PDFIX_AUTHORIZATION_FAILED: int = 22
EC_PDFIX_FAILED_TO_READ: int = 23
EC_PDFIX_FAILED_TO_OPEN: int = 24
EC_PDFIX_FAILED_TO_SAVE: int = 25
EC_PDFIX_FAILED_TO_SAVE_LANG: int = 26
EC_PDFIX_FAILED_TO_LOAD_TEMPLATE: int = 27

EC_FAILED_TO_OBTAIN_TEXT: int = 30
EC_FAILED_TO_DETECT_LANG: int = 31

MESSAGE_ARG_GENERAL: str = "Failed to parse arguments. Please check the usage and try again."
MESSAGE_ARG_INVALID_REGEX_OR_TEMPLATE: str = "Invalid regex or template. Please check the usage and try again."

MESSAGE_PDFIX_INITIALIZE: str = "Failed to initialize PDFix SDK."
MESSAGE_PDFIX_ACTIVATION_FAILED: str = "Failed to activate PDFix SDK acount."
MESSAGE_PDFIX_AUTHORIZATION_FAILED: str = "Failed to authorize PDFix SDK acount."
MESSAGE_PDFIX_FAILED_TO_READ: str = "Failed to read PDF document."
MESSAGE_PDFIX_FAILED_TO_OPEN: str = "Failed to open PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE: str = "Failed to save PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE_LANG: str = "Failed to set language to PDF document."
MESSAGE_PDFIX_FAILED_TO_LOAD_TEMPLATE: str = "Failed to load template file."

MESSAGE_FAILED_TO_OBTAIN_TEXT: str = "No words were extracted from input."
MESSAGE_FAILED_TO_DETECT_LANG: str = "No language was detected, not setting it to PDF."


class ExpectedException(BaseException):
    def __init__(self, error_code: int) -> None:
        self.error_code: int = error_code
        self.message: str = ""

    def _add_note(self, note: str) -> None:
        self.message = note


class ArgumentException(ExpectedException):
    def __init__(self, message: str = MESSAGE_ARG_GENERAL, error_code: int = EC_ARG_GENERAL) -> None:
        super().__init__(error_code)
        self._add_note(message)


class InvalidRegexOrTemplateException(ArgumentException):
    def __init__(self) -> None:
        super().__init__(MESSAGE_ARG_INVALID_REGEX_OR_TEMPLATE, EC_ARG_INVALID_REGEX_OR_TEMPLATE)


class PdfixInitializeException(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_PDFIX_INITIALIZE)
        self._add_note(MESSAGE_PDFIX_INITIALIZE)


class PdfixException(ExpectedException):
    def __init__(self, pdfix: Pdfix, error_code: int, message: str = "") -> None:
        super().__init__(error_code)
        pdfix_error_code: int = pdfix.GetErrorType()
        pdfix_error: str = str(pdfix.GetError())
        self.add_note(
            f"[{pdfix_error_code}] [{pdfix_error}]: {message}"
            if len(message) > 0
            else f"[{pdfix_error_code}] {pdfix_error}"
        )


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


class FailToExtractWordsException(DetectLanguageException):
    def __init__(self) -> None:
        super().__init__(EC_FAILED_TO_OBTAIN_TEXT, MESSAGE_FAILED_TO_OBTAIN_TEXT)


class FailToDetectLangException(DetectLanguageException):
    def __init__(self) -> None:
        super().__init__(EC_FAILED_TO_DETECT_LANG, MESSAGE_FAILED_TO_DETECT_LANG)
