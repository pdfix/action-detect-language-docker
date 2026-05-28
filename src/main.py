import argparse
import sys
import threading
import traceback
from pathlib import Path

from constants import CONFIG_FILE
from exceptions import (
    EC_ARG_GENERAL,
    MESSAGE_ARG_GENERAL,
    ExpectedException,
)
from extract_text import ExtractText
from image_update import DockerImageContainerUpdateChecker
from params_parser import ParamsParser
from set_doc_metadata import SetDocMetadata
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


def run_set_doc_metadata_subcommand(args) -> None:
    set_doc_metadata(args.input, args.output, args.name, args.key)


def set_doc_metadata(input_path: str, output_path: str, license_name: str, license_key: str) -> None:
    """
    Set language to document metadata on a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    set_doc_metadata = SetDocMetadata(license_name, license_key, input_path, output_path)
    set_doc_metadata.set_doc_metadata()


def run_set_tag_language_subcommand(args) -> None:
    set_tag_language(args.input, args.template, args.output, args.name, args.key)


def set_tag_language(
    input_path: str, template_path: str, output_path: str, license_name: str, license_key: str
) -> None:
    """
    Set language to chosen tags in a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        template_path (string): Path to the template file.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
    """
    set_tag_language = SetTagLanguage(license_name, license_key, template_path, input_path, output_path)
    set_tag_language.set_tag_language()


def run_extract_text_subcommand(args) -> None:
    extract_text(args.input, args.output)


def extract_text(input_path: str, output_path: str) -> None:
    """
    Extract text from a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the extracted text.
    """
    extract_text = ExtractText(input_path, output_path)
    extract_text.extract_text()


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

    # PDF set doc metadata subparser
    set_doc_metadata_subparser = subparsers.add_parser(
        "set-doc-metadata", help="Set language to document metadata on a PDF document"
    )
    set_arguments(
        set_doc_metadata_subparser,
        ["name", "key", "input", "output"],
        True,
        "The PDF document.",
    )
    set_doc_metadata_subparser.set_defaults(func=run_set_doc_metadata_subcommand)

    # PDF set tag language subparser
    # TODO parse params file argument, feed it to parser a provide path to internal template file as template json file
    set_tag_language_subparser = subparsers.add_parser(
        "set-tag-language", help="Set language to chosen tags in a PDF document"
    )
    set_arguments(
        set_tag_language_subparser,
        ["name", "key", "input", "template", "output"],
        True,
        "The PDF document.",
    )
    set_tag_language_subparser.set_defaults(func=run_set_tag_language_subcommand)
    # TODO add clean up where needed

    # PDF extract text subparser
    extract_text_subparser = subparsers.add_parser(
        "extract-text", help="Extract text from a PDF document or text file or input and write it to a text file."
    )
    set_arguments(
        extract_text_subparser,
        ["input", "output"],
        True,
        "The text file.",
    )
    extract_text_subparser.set_defaults(func=run_extract_text_subcommand)

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
