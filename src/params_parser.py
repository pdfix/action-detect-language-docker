import json
import logging
import os
import tempfile
from typing import Any, TextIO, cast

from logger import get_logger

logger: logging.Logger = get_logger("app_logger")


class ParamsParser:
    def __init__(self, params_json_path: str) -> None:
        self.params_json_path: str = params_json_path
        self.params: dict[str, Any] = {}
        self.template_json_path: str = ""

    def parse(self) -> None:
        with open(self.params_json_path, "r") as file:
            json_data: Any = json.load(file)

            if isinstance(json_data, dict):
                params_data: Any = json_data.get("params")

                if isinstance(params_data, dict):
                    self._parse_dictionary_item(params_data)
                elif isinstance(params_data, list):
                    for item in params_data:
                        if isinstance(item, dict):
                            self._parse_dictionary_item(item)
                        else:
                            logger.error(f"No expecting '{type(item)}' under list for params.")
                else:
                    logger.error(f"Invalid params data: {type(params_data)}")
            else:
                logger.error(f"Invalid json data: {type(json_data)}")

        # Create template JSON file if needed
        self._create_template_json_file()

    def clean_up(self) -> None:
        if self.template_json_path:
            os.remove(self.template_json_path)

    def _parse_dictionary_item(self, dict_item: dict[Any, Any]) -> None:
        for key, value in dict_item.items():
            if isinstance(key, str):
                self.params[key] = value
            else:
                logger.error(f"Invalid key type '{type(key)}' in params")

    def _create_template_json_file(self) -> None:
        template_data: Any = None

        if "object_types" in self.params:
            logger.debug("Found template data in 'object_types' key")
            template_data = self.params.get("object_types")
        elif "object" in self.params:
            logger.debug("Found template data in 'object' key")
            template_data = self.params.get("object")

        if template_data is not None:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                delete=False,
                suffix=".json",
            ) as temp_file_raw:
                temp_file: TextIO = cast(TextIO, temp_file_raw)
                self.template_json_path = temp_file.name
                logger.debug(f"Creating template JSON file in: {self.template_json_path}")
                json.dump(template_data, temp_file)
                temp_file.flush()
