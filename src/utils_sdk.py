import logging
from typing import Optional

from pdfixsdk import Pdfix, PsAccountAuthorization, PsStandardAuthorization

from exceptions import PdfixActivationException, PdfixAuthorizationException
from logger import get_logger

logger: logging.Logger = get_logger("app_logger")


def authorize_sdk(pdfix: Pdfix, license_name: str, license_key: str) -> None:
    """
    Tries to authorize or activate Pdfix license.

    Args:
        pdfix (Pdfix): Pdfix sdk instance.
        license_name (string): Pdfix sdk license name (e-mail)
        license_key (string): Pdfix sdk license key
    """

    # @KA:action pdfix_detect_pdf_language_langdetect pdfix_detect_tag_language_to_pdf_langdetect
    # pdfix_detect_content_language_to_pdf_langdetect
    # @KA:logic PDFix license
    # @KA:desc The license name and key from PDFix Desktop are used to authorize PDFix SDK. Without a
    # license the trial is used, which adds watermarks and may redact random content in the output
    # PDF, and the redacted text can change the detected language.
    # @KA:problem "Failed to authorize PDFix SDK account." (error 22) or activation failed (error 21)
    # @KA:solution The license name or key is not valid. Check the license in PDFix Desktop settings.
    if license_name and license_key:
        authorization: Optional[PsAccountAuthorization] = pdfix.GetAccountAuthorization()
        if authorization is None or not authorization.Authorize(license_name, license_key):
            raise PdfixAuthorizationException(pdfix)
    elif license_key:
        standard_authorization: Optional[PsStandardAuthorization] = pdfix.GetStandardAuthorization()
        if standard_authorization is None or not standard_authorization.Activate(license_key):
            raise PdfixActivationException(pdfix)
    else:
        logger.info("No license name or key provided. Using PDFix SDK trial")
