from pdfixsdk import Pdfix

EC_ARG_GENERAL = 10

EC_PDFIX_INITIALIZE = 20
EC_PDFIX_ACTIVATION_FAILED = 21
EC_PDFIX_AUTHORIZATION_FAILED = 22
EC_PDFIX_FAILED_TO_READ = 23
EC_PDFIX_FAILED_TO_OPEN = 24
EC_PDFIX_FAILED_TO_SAVE = 25
EC_PDFIX_FAILED_TO_SAVE_LANG = 26

EC_FAILED_TO_OBTAIN_TEXT = 30
EC_FAILED_TO_DETECT_LANG = 31

MESSAGE_ARG_GENERAL = "Failed to parse arguments. Please check the usage and try again."

MESSAGE_PDFIX_INITIALIZE = "Failed to initialize PDFix SDK."
MESSAGE_PDFIX_ACTIVATION_FAILED = "Failed to activate PDFix SDK acount."
MESSAGE_PDFIX_AUTHORIZATION_FAILED = "Failed to authorize PDFix SDK acount."
MESSAGE_PDFIX_FAILED_TO_READ = "Failed to read PDF document."
MESSAGE_PDFIX_FAILED_TO_OPEN = "Failed to open PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE = "Failed to save PDF document."
MESSAGE_PDFIX_FAILED_TO_SAVE_LANG = "Failed to set language to PDF document."

MESSAGE_FAILED_TO_OBTAIN_TEXT = "No words were extracted from input."
MESSAGE_FAILED_TO_DETECT_LANG = "No language was detected, not setting it to PDF."


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


class PdfixInitializeException(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_PDFIX_INITIALIZE)
        self._add_note(MESSAGE_PDFIX_INITIALIZE)


class PdfixException(Exception):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        error_code = pdfix.GetErrorType()
        error = str(pdfix.GetError())
        self.errno = error_code
        self.add_note(f"[{error_code}] [{error}]: {message}" if len(message) > 0 else f"[{error_code}] {error}")


class PdfixActivationException(PdfixException):
    def __init__(self, pdfix: Pdfix) -> None:
        super().__init__(pdfix, MESSAGE_PDFIX_ACTIVATION_FAILED)
        self.error_code = EC_PDFIX_ACTIVATION_FAILED


class PdfixAuthorizationException(PdfixException):
    def __init__(self, pdfix: Pdfix) -> None:
        super().__init__(pdfix, MESSAGE_PDFIX_AUTHORIZATION_FAILED)
        self.error_code = EC_PDFIX_AUTHORIZATION_FAILED


class PdfixFailedToReadException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, f"{MESSAGE_PDFIX_FAILED_TO_READ} {message}")
        self.error_code = EC_PDFIX_FAILED_TO_READ


class PdfixFailedToOpenException(PdfixException):
    def __init__(self, pdfix: Pdfix, pdf_path: str = "") -> None:
        super().__init__(pdfix, f"{MESSAGE_PDFIX_FAILED_TO_OPEN} {pdf_path}")
        self.error_code = EC_PDFIX_FAILED_TO_OPEN


class PdfixFailedToSaveException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, f"{MESSAGE_PDFIX_FAILED_TO_SAVE} {message}")
        self.error_code = EC_PDFIX_FAILED_TO_SAVE


class PdfixFailedToSaveLanguageException(PdfixException):
    def __init__(self, pdfix: Pdfix, message: str = "") -> None:
        super().__init__(pdfix, f"{MESSAGE_PDFIX_FAILED_TO_SAVE_LANG} {message}")
        self.error_code = EC_PDFIX_FAILED_TO_SAVE_LANG


class FailToExtractWordsException(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_FAILED_TO_OBTAIN_TEXT)
        self._add_note(MESSAGE_FAILED_TO_OBTAIN_TEXT)


class FailToDetectLangException(ExpectedException):
    def __init__(self) -> None:
        super().__init__(EC_FAILED_TO_DETECT_LANG)
        self._add_note(MESSAGE_FAILED_TO_DETECT_LANG)
