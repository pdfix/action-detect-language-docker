import argparse
import os
import sys
import traceback
from pathlib import Path

from image_update import DockerImageContainerUpdateChecker
from lang_detect import DetectLanguage


def set_arguments(
    parser: argparse.ArgumentParser,
    names: list,
    required_output: bool = True,
    output_help: str = "",
) -> None:
    """
    Set arguments for the parser based on the provided names and options.

    Args:
        parser (argparse.ArgumentParser): The argument parser to set arguments for.
        names (list): List of argument names to set.
        required_output (bool): Whether the output argument is required. Defaults to True.
        output_help (str): Help for argument output. Defaults to "".
    """
    for name in names:
        match name:
            case "input":
                parser.add_argument(
                    "--input", "-i", type=str, required=True, help="The input PDF or TXT file or text to detect."
                )
            case "key":
                parser.add_argument("--key", type=str, help="PDFix license key.")
            case "name":
                parser.add_argument("--name", type=str, help="PDFix license name.")
            case "output":
                parser.add_argument("--output", "-o", type=str, required=required_output, help=output_help)


def run_config_subcommand(args) -> None:
    get_pdfix_config(args.output)


def get_pdfix_config(path: str) -> None:
    """
    If Path is not provided, output content of config.
    If Path is provided, copy config to destination path.

    Args:
        path (str): Destination path for config.json file
    """
    config_path = os.path.join(Path(__file__).parent.absolute(), "../config.json")

    with open(config_path, "r", encoding="utf-8") as file:
        if path is None:
            print(file.read())
        else:
            with open(path, "w") as out:
                out.write(file.read())


def run_lang_detect_subcommand(args) -> None:
    detect_lang(args.input, args.output, args.name, args.key)


def detect_lang(input: str, output_path: str, license_name: str, license_key: str) -> None:
    """
    Detects language from input and writes it to output.
    If output is txt it writes language string into it.
    If output is pdf it sets language for it.

    Args:
        input (string): Path or text.
        output_path (string): Path.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    detect_language = DetectLanguage(license_name, license_key, input, output_path)
    detect_language.detect()


def main() -> None:  # noqa: D103
    parser = argparse.ArgumentParser(
        description="Identify a language from PDF or text file.",
    )

    subparsers = parser.add_subparsers(dest="subparser")

    # Config subparser
    config_subparser = subparsers.add_parser("config", help="Extract config file for integration")
    set_arguments(
        config_subparser,
        ["output"],
        False,
        "Output to save the config JSON file. Application output is used if not provided.",
    )
    config_subparser.set_defaults(func=run_config_subcommand)

    # Language detect subparser
    language_detect_help = "Detect language of a PDF or text provided in the input. "
    language_detect_help += "The detected language is printed as an output. "
    language_detect_help += "Allowed combinations are: "
    language_detect_help += "1. PDF -> PDF. "
    language_detect_help += "2. PDF -> TXT. "
    language_detect_help += "3. TXT -> TXT. "
    language_detect_help += "4. input argument -> TXT."
    lang_detect_subparser = subparsers.add_parser("lang-detect", help=language_detect_help)
    set_arguments(
        lang_detect_subparser,
        ["name", "key", "input", "output"],
        True,
        "Output to save a PDF documet or TXT file according to input.",
    )
    lang_detect_subparser.set_defaults(func=run_lang_detect_subcommand)

    # Parse arguments
    try:
        args = parser.parse_args()
    except SystemExit as e:
        if e.code == 0:
            # This happens when --help is used, exit gracefully
            sys.exit(0)
        print("Failed to parse arguments. Please check the usage and try again.", file=sys.stderr)
        sys.exit(e.code)

    # Update of docker image checker
    update_checker = DockerImageContainerUpdateChecker()
    update_checker.check_for_image_updates()

    if hasattr(args, "func"):
        # Run subcommand
        try:
            args.func(args)
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Failed to run the program: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
