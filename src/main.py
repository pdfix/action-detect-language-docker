import argparse
import json
import logging
import sys
import tempfile
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from constants import CONFIG_FILE
from detect_language import DetectLanguage
from exceptions import (
    EC_ARG_GENERAL,
    MESSAGE_ARG_GENERAL,
    ArgumentException,
    ArgumentInputNotTxtException,
    ArgumentOutputFolderNotExistsException,
    ExpectedException,
    InvalidRegexOrTemplateException,
)
from image_update import DockerImageContainerUpdateChecker
from logger import get_logger
from params_parser import ParamsParser
from set_content_language import SetContentLanguage
from set_document_language import SetDocumentLanguage
from set_tag_language import SetTagLanguage

logger: logging.Logger = get_logger("app_logger")


def str2bool(value: Any) -> bool:
    """
    Helper function to convert argument to boolean.

    Args:
        value (Any): The value to convert to boolean.

    Returns:
        Parsed argument as boolean.
    """
    if isinstance(value, bool):
        return value
    if value.lower() in ("yes", "true", "t", "1"):
        return True
    elif value.lower() in ("no", "false", "f", "0"):
        return False
    else:
        raise ArgumentException(f"{MESSAGE_ARG_GENERAL} Boolean value expected.")


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
            case "default_language":
                parser.add_argument(
                    "--default-language",
                    type=str,
                    default="",
                    help="Language applied when detection is not reliable (short text, numbers only). "
                    "Defaults to the document language, or en if the document has none.",
                )
            case "input":
                parser.add_argument("--input", "-i", type=str, required=True, help="The input PDF or TXT file.")
            case "key":
                parser.add_argument("--key", type=str, default="", nargs="?", help="PDFix license key.")
            case "maxwords":
                parser.add_argument(
                    "--maxwords", type=int, default=100, help="How many words are considered for language detection."
                )
            case "name":
                parser.add_argument("--name", type=str, default="", nargs="?", help="PDFix license name.")
            case "output":
                parser.add_argument("--output", "-o", type=str, required=required_output, help=output_help)
            case "overwrite":
                parser.add_argument(
                    "--overwrite", type=str2bool, default=False, help="Overwrite already existing language."
                )
            case "params":
                parser.add_argument(
                    "--params", type=str, required=True, help="Path to JSON file with filled parameters."
                )


def check_output_folder(output_path: str) -> None:
    """
    Check that the folder for the output file exists before any processing.

    Args:
        output_path (str): Path to the output file.
    """
    output_folder: Path = Path(output_path).resolve().parent
    if not output_folder.is_dir():
        raise ArgumentOutputFolderNotExistsException(output_folder.as_posix())


def run_config_subcommand(args) -> None:
    get_pdfix_config(args.output)


def get_pdfix_config(path: Optional[str]) -> None:
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
    check_output_folder(args.output)
    set_document_language(args.input, args.output, args.name, args.key, args.maxwords, args.overwrite)


def set_document_language(
    input_path: str, output_path: str, license_name: str, license_key: str, maxwords: int, overwrite: bool
) -> None:
    """
    Set language to document metadata on a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
        maxwords (int): How many words are considered for language detection.
        overwrite (bool): Whether to overwrite already existing document language.
    """
    set_document_language = SetDocumentLanguage(license_name, license_key, input_path, output_path, maxwords, overwrite)
    set_document_language.set_document_language()


def run_set_tag_language_subcommand(args) -> None:
    check_output_folder(args.output)
    params_parser = ParamsParser(args.params)
    params_parser.parse()
    tag_names: Any = params_parser.get("tag_names")
    if isinstance(tag_names, str):
        regex_pattern: str = tag_names
        set_tag_language(
            args.input,
            args.output,
            args.name,
            args.key,
            args.maxwords,
            args.overwrite,
            regex_pattern,
            args.default_language,
        )
    elif isinstance(tag_names, dict):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json") as template_file:
            with open(template_file.name, "w", encoding="utf-8") as template_file_write:
                json.dump(tag_names, template_file_write)
            template_path: Path = Path(template_file.name)
            set_tag_language(
                args.input,
                args.output,
                args.name,
                args.key,
                args.maxwords,
                args.overwrite,
                template_path,
                args.default_language,
            )
    else:
        raise InvalidRegexOrTemplateException()


def set_tag_language(
    input_path: str,
    output_path: str,
    license_name: str,
    license_key: str,
    maxwords: int,
    overwrite: bool,
    regex_template: str | Path,
    default_language: str,
) -> None:
    """
    Set language to chosen tags in a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
        maxwords (int): How many words are considered for language detection.
        overwrite (bool): Whether to overwrite already existing language.
        regex_template (str | Path): Either regex or path to the template JSON file.
        default_language (str): Language applied when detection is not reliable, can be empty.
    """
    set_tag_language = SetTagLanguage(
        license_name, license_key, input_path, regex_template, output_path, maxwords, overwrite, default_language
    )
    set_tag_language.set_tag_language()


def run_set_content_language_subcommand(args) -> None:
    check_output_folder(args.output)
    params_parser = ParamsParser(args.params)
    params_parser.parse()
    object_types: Any = params_parser.get("object_types")
    if isinstance(object_types, str):
        regex_pattern: str = object_types
        set_content_language(
            args.input,
            args.output,
            args.name,
            args.key,
            args.maxwords,
            args.overwrite,
            regex_pattern,
            args.default_language,
        )
    elif isinstance(object_types, dict):
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", suffix=".json") as template_file:
            with open(template_file.name, "w", encoding="utf-8") as template_file_write:
                json.dump(object_types, template_file_write)
            template_path: Path = Path(template_file.name)
            set_content_language(
                args.input,
                args.output,
                args.name,
                args.key,
                args.maxwords,
                args.overwrite,
                template_path,
                args.default_language,
            )
    else:
        raise InvalidRegexOrTemplateException()


def set_content_language(
    input_path: str,
    output_path: str,
    license_name: str,
    license_key: str,
    maxwords: int,
    overwrite: bool,
    regex_template: str | Path,
    default_language: str,
) -> None:
    """
    Set language to chosen content in a PDF document.

    Args:
        input_path (string): Path to the PDF document.
        output_path (string): Path to save the PDF document.
        license_name (string): Pdfix sdk license name (e-mail).
        license_key (string): Pdfix sdk license key.
        maxwords (int): How many words are considered for language detection.
        overwrite (bool): Whether to overwrite already existing language.
        regex_template (str | Path): Either regex or path to the template JSON file.
        default_language (str): Language applied when detection is not reliable, can be empty.
    """
    set_content_language = SetContentLanguage(
        license_name, license_key, input_path, regex_template, output_path, maxwords, overwrite, default_language
    )
    set_content_language.set_content_language()


def run_detect_language_subcommand(args) -> None:
    check_output_folder(args.output)
    input_path: Path = Path(args.input)
    if input_path.suffix.lower() != ".txt" or not input_path.is_file():
        raise ArgumentInputNotTxtException(args.input)
    detect_language(args.input, args.output, args.maxwords)


def detect_language(input_path: str, output_path: str, maxwords: int) -> None:
    """
    Detect language from a text file and write it to a text file.

    Args:
        input_path (string): Path to the TXT file.
        output_path (string): Path to save the extracted text.
        maxwords (int): How many words are considered for language detection.
    """
    detect_language = DetectLanguage(input_path, output_path, maxwords)
    detect_language.detect_language()


def main() -> None:  # noqa: D103
    parser = argparse.ArgumentParser(
        description="Identify a language from PDF or text file.",
    )

    subparsers = parser.add_subparsers(title="Commands", dest="command", required=True)

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
        ["name", "key", "input", "output", "maxwords", "overwrite"],
        True,
        "The PDF document.",
    )
    # Document language is replaced by default
    set_document_language_subparser.set_defaults(func=run_set_document_language_subcommand, overwrite=True)

    # PDF set tag language subparser
    set_tag_language_subparser = subparsers.add_parser(
        "set-tag-language", help="Set language to chosen tags in a PDF document"
    )
    set_arguments(
        set_tag_language_subparser,
        ["name", "key", "input", "output", "maxwords", "overwrite", "default_language", "params"],
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
        ["name", "key", "input", "output", "maxwords", "overwrite", "default_language", "params"],
        True,
        "The PDF document.",
    )
    set_content_language_subparser.set_defaults(func=run_set_content_language_subcommand)

    # Detect language subparser
    detect_language_subparser = subparsers.add_parser(
        "detect-language", help="Detect language from a TXT file and write the language code to a TXT file."
    )
    set_arguments(
        detect_language_subparser,
        ["input", "output", "maxwords"],
        True,
        "The text file.",
    )
    detect_language_subparser.set_defaults(func=run_detect_language_subcommand)

    # Parse arguments
    try:
        args = parser.parse_args()
    except ExpectedException as e:
        logger.error(e.message)
        sys.exit(e.error_code)
    except SystemExit as e:
        if e.code != 0:
            logger.error(MESSAGE_ARG_GENERAL)
            sys.exit(EC_ARG_GENERAL)
        # This happens when --help is used, exit gracefully
        sys.exit(0)
    except Exception as e:
        logger.error("Failed to run the program:")
        logger.exception(e)
        sys.exit(1)

    if hasattr(args, "func"):
        # Check for updates only when help is not checked
        update_checker = DockerImageContainerUpdateChecker()
        # Check it in separate thread not to be delayed when there is slow or no internet connection
        update_thread = threading.Thread(target=update_checker.check_for_image_updates)
        update_thread.start()

        # Measure the time it takes to process the input
        start_time: float = time.time()
        current_time: str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        logger.info(f"Processing started at: {current_time}")

        # Run subcommand
        try:
            args.func(args)
        except ExpectedException as e:
            logger.error(e.message)
            if e.sdk_error:
                logger.error(e.sdk_error)
            sys.exit(e.error_code)
        except Exception as e:
            # not expected exception -> print stack trace and what exception happened
            logger.error("Failed to run the program:")
            logger.exception(e)
            sys.exit(1)
        finally:
            elapsed_time: float = time.time() - start_time
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            logger.info(f"Processing finished at: {current_time}. Elapsed time: {elapsed_time:.2f} seconds")

            # Make sure to let update thread finish before exiting
            update_thread.join()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
