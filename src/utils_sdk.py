from pdfixsdk import Pdfix


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
            error_code = pdfix.GetErrorType()
            error = str(pdfix.GetError())
            raise Exception(f"[{error_code}] Authorization failed: {error}")
    elif license_key:
        if not pdfix.GetStandarsAuthorization().Activate(license_key):
            error_code = pdfix.GetErrorType()
            error = str(pdfix.GetError())
            raise Exception(f"[{error_code}] Activation failed: {error}")
    else:
        print("No license name or key provided. Using PDFix SDK trial")
