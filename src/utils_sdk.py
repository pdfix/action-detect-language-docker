import functools
import logging
from ctypes import CFUNCTYPE, c_int, c_void_p
from typing import Callable, Optional, TypeAlias

from pdfixsdk import Pdfix, PsAccountAuthorization, PsStandardAuthorization

from exceptions import PdfixActivationException, PdfixAuthorizationException
from logger import get_logger

logger: logging.Logger = get_logger("app_logger")

# Workaround for pdfix-sdk <= 9.1.1: generated bindings declare the callback as c_int.
StructElemEnumProcType = CFUNCTYPE(c_int, c_void_p, c_void_p, c_int, c_void_p)
PageObjectEnumProcType = CFUNCTYPE(c_int, c_void_p, c_int, c_void_p)

# Mypy cannot treat CFUNCTYPE(...) results as types; use these for annotations.
StructElemEnumProcCallback: TypeAlias = Callable[..., int]
PageObjectEnumProcCallback: TypeAlias = Callable[..., int]


def get_pdfix_lib():
    from pdfixsdk.Pdfix import PdfixLib

    if PdfixLib is None:
        raise RuntimeError("PdfixLib is not initialized")
    return PdfixLib


@functools.lru_cache(maxsize=1)
def ensure_enum_struct_tree_argtypes() -> None:
    pdfix_lib = get_pdfix_lib()
    pdfix_lib.PdfDocEnumStructTree.restype = c_int
    pdfix_lib.PdfDocEnumStructTree.argtypes = [
        c_void_p,
        c_void_p,
        c_int,
        StructElemEnumProcType,
        c_void_p,
    ]


@functools.lru_cache(maxsize=1)
def ensure_enum_page_objects_argtypes() -> None:
    pdfix_lib = get_pdfix_lib()
    pdfix_lib.PdfDocEnumPageObjects.restype = c_int
    pdfix_lib.PdfDocEnumPageObjects.argtypes = [
        c_void_p,
        c_void_p,
        c_void_p,
        c_int,
        PageObjectEnumProcType,
        c_void_p,
    ]


def authorize_sdk(pdfix: Pdfix, license_name: str, license_key: str) -> None:
    """
    Tries to authorize or activate Pdfix license.

    Args:
        pdfix (Pdfix): Pdfix sdk instance.
        license_name (string): Pdfix sdk license name (e-mail)
        license_key (string): Pdfix sdk license key
    """

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
