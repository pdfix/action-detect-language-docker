import argparse
import sys
import threading
import traceback
from pathlib import Path

from constants import CONFIG_FILE
from detect_language import DetectLanguage
from exceptions import (
    EC_ARG_GENERAL,
    MESSAGE_ARG_GENERAL,
    ExpectedException,
)
from image_update import DockerImageContainerUpdateChecker
from params_parser import ParamsParser
from set_content_language import SetContentLanguage
from set_document_language import SetDocumentLanguage
from set_tag_language import SetTagLanguage


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
                parser.add_argument("--key", type=str, default="", nargs="?", help="PDFix license key.")
            case "name":
                parser.add_argument("--name", type=str, default="", nargs="?", help="PDFix license name.")
            case "output":
                parser.add_argument("--output", "-o", type=str, required=required_output, help=output_help)
            case "template":
                parser.add_argument("--template", "-t", type=str, required=True, help="Template file path.")


def run_config_subcommand(args) -> None:
    get_pdfix_config(args.output)


def get_pdfix_config(path: str) -> None:
    """
    If Path is not provided, output content of config.
    If Path is provided, copy config to destination path.

    Args:
        path (str): Destination path for config.json file
    """
    config_path: Path = Path(__file__).parent.parent.joinpath(CONFIG_FILE)

    with open(config_path, "r", encoding="utf-8") as file:
        if path is None:
            print(file.read())
        else:
            with open(path, "w") as out:
                out.write(file.read())


def run_set_document_language_subcommand(args) -> None:
    set_document_language(args.input, args.output, args.name, args.key)


def set_document_language(input_path: str, output_path: str, license_name: str, license_key: str) -> None:
    """
    Set language to document metadata on a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    set_document_language = SetDocumentLanguage(license_name, license_key, input_path, output_path)
    set_document_language.set_document_language()


def run_set_tag_language_subcommand(args) -> None:
    # TODO parse params file argument, feed it to parser a provide path to internal template file as template json file
    # TODO add clean up where needed
    params_parser = ParamsParser("")
    params_parser.clean_up()
    set_tag_language(args.input, args.output, args.name, args.key)


def set_tag_language(input_path: str, output_path: str, license_name: str, license_key: str) -> None:
    """
    Set language to chosen tags in a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    # TODO
    template_path: str = ""
    set_tag_language = SetTagLanguage(license_name, license_key, input_path, template_path, output_path)
    set_tag_language.set_tag_language()


def run_set_content_language_subcommand(args) -> None:
    # TODO parse params file argument, feed it to parser a provide path to internal template file as template json file
    # TODO add clean up where needed
    params_parser = ParamsParser("")
    params_parser.clean_up()
    set_content_language(args.input, args.output, args.name, args.key)


def set_content_language(input_path: str, output_path: str, license_name: str, license_key: str) -> None:
    """
    Set language to chosen content in a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    # TODO
    template_path: str = ""
    set_content_language = SetContentLanguage(license_name, license_key, input_path, template_path, output_path)
    set_content_language.set_content_language()


def run_detect_language_subcommand(args) -> None:
    detect_language(args.input, args.output)


def detect_language(input_path: str, output_path: str) -> None:
    """
    Detect language from a text file or input and write it to a text file.

    Args:
        input_path (string): Path to the TXT file or input.
        output_path (string): Path to save the extracted text.
    """
    detect_language = DetectLanguage(input_path, output_path)
    detect_language.detect_language()


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

    # PDF set document language subparser
    set_document_language_subparser = subparsers.add_parser(
        "set-document-language", help="Set language to document metadata on a PDF document"
    )
    set_arguments(
        set_document_language_subparser,
        ["name", "key", "input", "output"],
        True,
        "The PDF document.",
    )
    set_document_language_subparser.set_defaults(func=run_set_document_language_subcommand)

    # PDF set tag language subparser
    set_tag_language_subparser = subparsers.add_parser(
        "set-tag-language", help="Set language to chosen tags in a PDF document"
    )
    set_arguments(
        set_tag_language_subparser,
        ["name", "key", "input", "output"],
        True,
        "The PDF document.",
    )
    set_tag_language_subparser.set_defaults(func=run_set_tag_language_subcommand)

    # PDF set content language subparser
    set_content_language_subparser = subparsers.add_parser(
        "set-content-language", help="Set language to chosen content in a PDF document"
    )
    set_arguments(
        set_content_language_subparser,
        ["name", "key", "input", "output"],
        True,
        "The PDF document.",
    )
    set_content_language_subparser.set_defaults(func=run_set_content_language_subcommand)

    # detect language subparser # TODO rename
    detect_language_subparser = subparsers.add_parser(
        "detect_language", help="Extract text from a text file or input and write it to a text file."
    )
    set_arguments(
        detect_language_subparser,
        ["input", "output"],
        True,
        "The text file.",
    )
    detect_language_subparser.set_defaults(func=run_detect_language_subcommand)

    # Parse arguments
    try:
        args = parser.parse_args()
    except ExpectedException as e:
        print(e.message, file=sys.stderr)
        sys.exit(e.error_code)
    except SystemExit as e:
        if e.code != 0:
            print(MESSAGE_ARG_GENERAL, file=sys.stderr)
            sys.exit(EC_ARG_GENERAL)
        # This happens when --help is used, exit gracefully
        sys.exit(0)
    except Exception as e:
        print(traceback.format_exc(), file=sys.stderr)
        print(f"Failed to run the program: {e}", file=sys.stderr)
        sys.exit(1)

    if hasattr(args, "func"):
        # Check for updates only when help is not checked
        update_checker = DockerImageContainerUpdateChecker()
        # Check it in separate thread not to be delayed when there is slow or no internet connection
        update_thread = threading.Thread(target=update_checker.check_for_image_updates)
        update_thread.start()

        # Run subcommand
        try:
            args.func(args)
        except ExpectedException as e:
            print(e.message, file=sys.stderr)
            sys.exit(e.error_code)
        except Exception as e:
            print(traceback.format_exc(), file=sys.stderr)
            print(f"Failed to run the program: {e}", file=sys.stderr)
            sys.exit(1)
        finally:
            # Make sure to let update thread finish before exiting
            update_thread.join()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
