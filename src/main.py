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

def get_config(path) -> None:    
    if path is None:
        with open(os.path.join(Path(__file__).parent.absolute(), "../config.json"), 'r') as f:
            print(f.read())    
    else:
        src = os.path.join(Path(__file__).parent.absolute(), "../config.json")
        dst = path
        shutil.copyfile(src, dst)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Identify a language from PDF or text file.",
    )
    parser.add_argument("--name", type=str, default="", help="license name")
    parser.add_argument("--key", type=str, default="", help="license key")

    subparsers = parser.add_subparsers(dest="subparser")

    # get config subparser
    pars_config = subparsers.add_parser("config", help="Extract config file for integration")
    pars_config.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output to save the config JSON file. Application output is used if not provided",
    )

    # lang-detect subparser
    lang_detect = subparsers.add_parser("lang-detect", help="Detect language of a PDF or text provided in the input. The detected languate is printed as an output.")
    lang_detect.add_argument("-i", "--input", type=str, help="The input PDF or text to detect", required=True)
    lang_detect.add_argument(
        "-o",
        "--output",
        type=str,
        help="Output to save a PDF documet if input is a PDF document.",
    )
    # args = parser.parse_args()
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 0:  # This happens when --help is used, exit gracefully
            sys.exit(0)
        print("Failed to parse arguments. Please check the usage and try again.")
        sys.exit(1)

    if args.subparser == "config":
        get_config(args.output)
        sys.exit(0)
    elif args.subparser == "lang-detect":
        if not args.input or not args.output:
            parser.error("The following arguments are required: -i/--input, -o/--output")

        input_file = args.input
        output_file = args.output

        if input_file.lower().endswith(".pdf") and output_file.lower().endswith(".pdf"):
            if not os.path.isfile(input_file):
                sys.exit(f"Error: The input file '{input_file}' does not exist.",)
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
    else:
        print(
            "Invalid command. See --help for more information.",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
