import argparse
import os
import shutil
import sys
from pathlib import Path

from lang_detect import (
    detect_lang_pdf_2_pdf,
    detect_lang_pdf_2_txt,
    detect_lang_str_2_txt,
    detect_lang_txt_2_txt,
)


def get_config(out_dir: str) -> None:
    tgt = os.path.join(Path(__file__).parent.absolute(), "../config.json")
    dst = os.path.join(out_dir, "config.json")
    shutil.copyfile(tgt, dst)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify a language from PDF or text file.",
    )
    parser.add_argument("-i", "--input", type=str, help="The input PDF or text file")
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="The output PDF or text file.\
        PDF output is only valid if input is also PDF.",
    )
    parser.add_argument("--name", type=str, default="", help="Pdfix license name")
    parser.add_argument("--key", type=str, default="", help="Pdfix license key")
    parser.add_argument(
        "--config",
        type=str,
        help="Save config file to local directory from docker",
    )
    args = parser.parse_args()

    if args.config:
        print("copy config.json: {}".format(args.config))
        get_config(args.config)
        sys.exit(0)

    if not args.input or not args.output:
        parser.error("The following arguments are required: -i/--input, -o/--output")

    input_file = args.input
    output_file = args.output

    if input_file.lower().endswith(".pdf") and output_file.lower().endswith(".pdf"):
        if not os.path.isfile(input_file):
            sys.exit(f"Error: The input file '{input_file}' does not exist.")
            return
        try:
            detect_lang_pdf_2_pdf(input_file, output_file, args.name, args.key)
        except Exception as e:
            sys.exit("Failed to run OCR: {}".format(e))

    elif input_file.lower().endswith(".pdf") and output_file.lower().endswith(".txt"):
        if not os.path.isfile(input_file):
            sys.exit(f"Error: The input file '{input_file}' does not exist.")
            return
        detect_lang_pdf_2_txt(input_file, output_file, args.name, args.key)
    elif input_file.lower().endswith(".txt") and output_file.lower().endswith(".txt"):
        if not os.path.isfile(input_file):
            sys.exit(f"Error: The input file '{input_file}' does not exist.")
            return
        detect_lang_txt_2_txt(input_file, output_file)
    elif output_file.lower().endswith(".txt"):
        detect_lang_str_2_txt(input_file, output_file)
    else:
        print(
            "Invalid input combination. See --help for more information.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
