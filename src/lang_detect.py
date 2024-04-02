import argparse
import os, sys, json
from langdetect import detect
from pdfixsdk.Pdfix import *
from pdfixsdk.Pdfix import GetPdfix


def detect_lang_for_text(text: str) -> str:
    return detect(text)


def getText(element, words):
    if words.len() > 100:
        return

    elemType = element.GetType()
    if kPdeText == elemType:
        textElem = PdeText(element.obj)
        text = textElem.GetText()
        words.append(text.split())
    else:
        count = element.GetNumChildren()
        if count == 0:
            return
        for i in range(0, count):
            child = element.GetChild(i)
            if child is not None:
                getText(child, words)


def detect_pdf_lang(path: str):
    pdfix = GetPdfix()
    if pdfix is None:
        raise Exception("Pdfix Initialization fail")

    major = pdfix.GetVersionMajor()
    minor = pdfix.GetVersionMinor()
    patch = pdfix.GetVersionPatch()
    print("PDFix SDK Version " + str(major) + "." + str(minor) + "." + str(patch))

    # ACCOUNT LICENSE

    # authorization using email and license key
    # account autorization must be used each time the SDK is used
    if not pdfix.GetAccountAuthorization().Authorize(
        "YOUR LICENSE NAME", "YOUR LICENSE KEY"
    ):
        print("dummy message: PDFix SDK not authorized")

    doc = pdfix.OpenDoc(path, "")
    if doc is None:
        raise Exception("Unable to open pdf : " + pdfix.GetError())

    for i in range(0, doc.GetNumPages()):
        # acquire page
        page = doc.AcquirePage(i)
        if page is None:
            raise Exception("Acquire Page fail : " + pdfix.GetError())

        # get the page map of the current page
        pageMap = page.AcquirePageMap()
        if pageMap is None:
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())
        if not pageMap.CreateElements(0, None):
            raise Exception("Acquire PageMap fail: " + pdfix.GetError())

        # get page container
        container = pageMap.GetElement()
        if container is None:
            raise Exception("Get page element failure : " + pdfix.GetError())

        words = []
        getText(container, words)

        lang = detect_lang_for_text(" ".join(words))
        print(lang)
        doc.SetInfo("Lang", lang)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text", help="Input text", type=str, required=False)
    parser.add_argument("--input_json", help="Input JSON file", required=False)
    parser.add_argument("--input_pdf", help="Input PDF file", required=False)
    parser.add_argument("--output", help="Output text file", required=True)
    args = parser.parse_args()

    if args.input_text:
        lang = detect_lang_for_text(args.input_text)
        if os.path.isabs(args.output):
            out = args.output
        else:
            out = os.path.join(os.path.dirname(__file__), args.output)

        if not os.path.exists(os.path.dirname(out)):
            os.makedirs(os.path.dirname(out))
        with open(out, "w") as f:
            f.write(lang)

    elif args.input_json:
        pass
    elif args.input_pdf:
        try:
            detect_pdf_lang(args.input_pdf)
        except Exception as e:
            print("Failed to detect PDF language. {}".format(e), file=sys.stderr)
    else:
        print("Missing input.")


if __name__ == "__main__":
    main()
