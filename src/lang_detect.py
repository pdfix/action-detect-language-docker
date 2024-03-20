import argparse


import os, sys, json
from langdetect import detect


def detect_text(text: str) -> str:
    return detect(text)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_text", help="Input text", type=str, required=False)
    parser.add_argument("--input_json", help="Input JSON file", required=False)
    parser.add_argument("--input_pdf", help="Input PDF file", required=False)
    parser.add_argument("--output", help="Output text file", required=True)
    args = parser.parse_args()

    if args.input_text:
        lang = detect_text(args.input_text)
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
        pass
    else:
        print("Missing input.")


if __name__ == "__main__":
    main()
