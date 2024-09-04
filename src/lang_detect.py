import os
import shutil
import sys
import tempfile
from collections import Counter

from langdetect import detect
from pdfixsdk.Pdfix import GetPdfix, PdeText, kPdeText, kSaveFull


class PdfixException(Exception):
    def __init__(self, message: str = "") -> None:
        self.errno = GetPdfix().GetErrorType()
        self.add_note(message if len(message) else str(GetPdfix().GetError()))


def detect_lang_for_text(text: str) -> str:
    return detect(text)


def get_text(element, words) -> None:
    if len(words) > 100:
        return

    elem_type = element.GetType()
    if kPdeText == elem_type:
        text_elem = PdeText(element.obj)
        text = text_elem.GetText()
        for w in text.split():
            words.append(w)
    else:
        count = element.GetNumChildren()
        if count == 0:
            return
        for i in range(0, count):
            child = element.GetChild(i)
            if child is not None:
                get_text(child, words)


def detect_lang_pdf_2_pdf(
    in_path: str, out_path: str, license_name: str, license_key: str
):
    pdfix = GetPdfix()
    if pdfix is None:
        raise Exception("Pdfix Initialization fail")

    if license_name and license_key:
        if not pdfix.GetAccountAuthorization().Authorize(license_name, license_key):
            raise Exception("Pdfix SDK Authorization fail")
    else:
        print("No license name or key provided. Using Pdfix trial")

    doc = pdfix.OpenDoc(in_path, "")
    if doc is None:
        raise Exception("Unable to open pdf : " + pdfix.GetError())

    lang_list = []

    for i in range(0, doc.GetNumPages()):
        # acquire page
        page = doc.AcquirePage(i)
        if page is None:
            raise Exception("Acquire Page fail : " + pdfix.GetError())

        # get the page map of the current page
        page_map = page.AcquirePageMap()
        if page_map is None:
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())
        if not page_map.CreateElements(0, None):
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())

        # get page container
        container = page_map.GetElement()
        if container is None:
            raise Exception("Get page element failure : " + pdfix.GetError())

        words: list[str] = []
        get_text(container, words)

        lang = detect_lang_for_text(" ".join(words))
        lang_list.append(lang)

    # Count the frequency of each string
    string_counts = Counter(lang_list)

    # Get the string(s) that occur the most
    most_common_lang = string_counts.most_common(1)

    print("Detected language: " + most_common_lang[0][0])

    if out_path.endswith(".pdf"):
        doc.SetLang(most_common_lang[0][0])

        # save pdf to temporary file
        temp_file = tempfile.NamedTemporaryFile()
        doc.Save(temp_file.name, kSaveFull)

        # close pdf
        doc.Close()

        # copy temp file to output path
        shutil.copyfile(temp_file.name, out_path)

        temp_file.close()

    else:
        if not os.path.exists(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(most_common_lang[0][0])
        
def detect_lang_pdf_2_txt(
    in_path: str,
    out_path: str,
    license_name: str,
    license_key: str,
) -> None:
    pdfix = GetPdfix()
    if pdfix is None:
        raise Exception("Pdfix Initialization fail")

    if license_name and license_key:
        if not pdfix.GetAccountAuthorization().Authorize(license_name, license_key):
            raise Exception("Pdfix Authorization fail")
    else:
        print("No license name or key provided. Using Pdfix trial")

    doc = pdfix.OpenDoc(in_path, "")
    if doc is None:
        raise Exception("Unable to open pdf : " + pdfix.GetError())

    lang_list = []

    for i in range(0, doc.GetNumPages()):
        # acquire page
        page = doc.AcquirePage(i)
        if page is None:
            raise Exception("Acquire Page fail : " + pdfix.GetError())

        # get the page map of the current page
        page_map = page.AcquirePageMap()
        if page_map is None:
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())
        if not page_map.CreateElements(0, None):
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())

        # get page container
        container = page_map.GetElement()
        if container is None:
            raise Exception("Get page element failure : " + pdfix.GetError())

        words: list[str] = []
        get_text(container, words)

        lang = detect_lang_for_text(" ".join(words))
        lang_list.append(lang)

    # Count the frequency of each string
    string_counts = Counter(lang_list)

    # Get the string(s) that occur the most
    most_common_lang = string_counts.most_common(1)

    print("Detected language: " + most_common_lang[0][0])

    if not os.path.exists(os.path.dirname(out_path)):
        os.makedirs(os.path.dirname(out_path))
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(most_common_lang[0][0])


def detect_lang_txt_2_txt(input: str, output: str) -> None:
    try:
        with open(input, "r", encoding="utf-8") as infile:
            text = infile.read()

        detected_language = detect_lang_for_text(text)

        print("Detected language: " + detected_language)

        with open(output, "w", encoding="utf-8") as outfile:
            outfile.write(detected_language)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)


def detect_lang_str_2_txt(input_text: str, output: str) -> None:
    try:
        # Detect the language of the input text
        detected_language = detect_lang_for_text(input_text)

        print("Detected language: " + detected_language)

        # Write the detected language to the output file
        with open(output, "w", encoding="utf-8") as outfile:
            outfile.write(detected_language)

    except Exception as e:
        print(f"An error occurred: {str(e)}", file=sys.stderr)
        sys.exit(1)
