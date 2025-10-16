from pdfixsdk import Pdfix

from exceptions import PdfixActivationException, PdfixAuthorizationException


def authorize_sdk(pdfix: Pdfix, license_name: str, license_key: str) -> None:
    """
    Tries to authorize or activate Pdfix license.

    Args:
        pdfix (Pdfix): Pdfix sdk instance.
        license_name (string): Pdfix sdk license name (e-mail)
        license_key (string): Pdfix sdk license key
    """

    if license_name and license_key:
        authorization = pdfix.GetAccountAuthorization()
        if not authorization.Authorize(license_name, license_key):
            raise PdfixAuthorizationException(pdfix)
    elif license_key:
        if not pdfix.GetStandarsAuthorization().Activate(license_key):
            raise PdfixActivationException(pdfix)
    else:
        print("No license name or key provided. Using PDFix SDK trial")
