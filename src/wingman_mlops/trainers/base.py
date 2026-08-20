from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Optional

from src.wingman_mlops.config import FineTuningConfig
from src.wingman_mlops.logger import LOGGER


class ModelTrainer(ABC):
    def __init__(self, config: FineTuningConfig, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or LOGGER
        self.output_dir = Path(config.output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @abstractmethod
    def train(self) -> Dict[str, Any]:
        pass
