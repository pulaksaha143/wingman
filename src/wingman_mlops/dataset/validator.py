from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Optional, Tuple

from src.wingman_mlops.exceptions import DatasetValidationError
from src.wingman_mlops.logger import LOGGER


class DatasetValidator:
    REQUIRED_KEYS: Tuple[str, ...] = ("prompt", "completion")

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or LOGGER

    def validate_file(self, file_path: str | Path) -> int:
        path = Path(file_path)
        if not path.exists():
            error_msg = f"Dataset file not found at path: {path.resolve()}"
            self.logger.error(error_msg)
            raise FileNotFoundError(error_msg)

        if not path.is_file():
            error_msg = f"Specified path is not a file: {path.resolve()}"
            self.logger.error(error_msg)
            raise DatasetValidationError(error_msg)

        valid_count = 0

        self.logger.info(f"Initiating validation for dataset: {path.name}")

        with open(path, "r", encoding="utf-8") as stream:
            for line_number, raw_line in enumerate(stream, start=1):
                clean_line = raw_line.strip()
                if not clean_line:
                    self.logger.warning(f"Blank line detected at line {line_number} in {path.name}; skipping.")
                    continue

                try:
                    record = json.loads(clean_line)
                except json.JSONDecodeError as exc:
                    error_msg = f"Invalid JSON syntax at {path.name}:{line_number} - {str(exc)}"
                    self.logger.error(error_msg)
                    raise DatasetValidationError(error_msg) from exc

                if not isinstance(record, dict):
                    error_msg = f"Expected JSON object at {path.name}:{line_number}, got {type(record).__name__}"
                    self.logger.error(error_msg)
                    raise DatasetValidationError(error_msg)

                for key in self.REQUIRED_KEYS:
                    if key not in record:
                        error_msg = f"Missing required key '{key}' at {path.name}:{line_number}"
                        self.logger.error(error_msg)
                        raise DatasetValidationError(error_msg)
                    
                    if not isinstance(record[key], str) or not record[key].strip():
                        error_msg = f"Key '{key}' must be a non-empty string at {path.name}:{line_number}"
                        self.logger.error(error_msg)
                        raise DatasetValidationError(error_msg)

                valid_count += 1

        if valid_count == 0:
            error_msg = f"Dataset file {path.name} contains zero valid training rows."
            self.logger.error(error_msg)
            raise DatasetValidationError(error_msg)

        self.logger.info(f"Validation successful for {path.name}: {valid_count} validated rows.")
        return valid_count
