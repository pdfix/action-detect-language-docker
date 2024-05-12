import argparse
from collections import Counter
import shutil
import os, sys, json
import tempfile
from langdetect import detect
from pdfixsdk.Pdfix import *
from pdfixsdk.Pdfix import GetPdfix

pdfix = GetPdfix()


def detect_lang_for_text(text: str) -> str:
    return detect(text)


def getText(element, words):
    if len(words) > 100:
        return

    elemType = element.GetType()
    if kPdeText == elemType:
        textElem = PdeText(element.obj)
        text = textElem.GetText()
        for w in text.split():
            words.append(w)
    else:
        count = element.GetNumChildren()
        if count == 0:
            return
        for i in range(0, count):
            child = element.GetChild(i)
            if child is not None:
                getText(child, words)


def detect_pdf_lang(in_path: str, out_path: str):
    if pdfix is None:
        raise Exception("Pdfix Initialization fail")

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
        # print(words)
        lang = detect_lang_for_text(" ".join(words))
        lang_list.append(lang)
        # print(lang)

    # Count the frequency of each string
    string_counts = Counter(lang_list)

    # Get the string(s) that occur the most
    most_common_lang = string_counts.most_common(1)

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
        with open(out_path, "w") as f:
            f.write(most_common_lang[0][0])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i", "--input", help="Input text or path to PDF file", type=str, required=True
    )
    parser.add_argument("-o", "--output", help="Output text file", required=True)
    parser.add_argument("--license-name", help="License name", required=False)
    parser.add_argument("--license-key", help="License key", required=False)
    args = parser.parse_args()

    if args.license_name and args.license_key:
        if not pdfix.GetAccountAuthorization().Authorize(
            args.license_name, args.license_key
        ):
            print("Failed to authorize PDFix SDK")

    inp = str(args.input)

    if os.path.isabs(args.output):
        out = args.output
    else:
        out = os.path.join(os.path.dirname(__file__), args.output)

    if inp.endswith(".pdf"):
        try:
            detect_pdf_lang(inp, out)
        except Exception as e:
            print("Failed to detect PDF language. {}".format(e), file=sys.stderr)

    elif inp.endswith(".json"):
        raise NotImplementedError

    else:
        lang = detect_lang_for_text(inp)
        if out.endswith(".pdf"):
            print("If input is plain text, output cannot be PDF file", file=sys.stderr)
            exit(1)
        if not os.path.exists(os.path.dirname(out)):
            os.makedirs(os.path.dirname(out))
        with open(out, "w") as f:
            f.write(lang)


if __name__ == "__main__":
    main()
