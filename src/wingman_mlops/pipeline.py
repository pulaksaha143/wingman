from __future__ import annotations

import json
import logging
import signal
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from src.wingman_mlops.config import FineTuningConfig
from src.wingman_mlops.dataset.validator import DatasetValidator
from src.wingman_mlops.logger import LOGGER
from src.wingman_mlops.trainers.base import ModelTrainer
from src.wingman_mlops.trainers.mlx_trainer import MLXModelTrainer
from src.wingman_mlops.trainers.torch_trainer import PyTorchMPSModelTrainer


class TrainingPipelineOrchestrator:
    def __init__(self, config: FineTuningConfig, logger: Optional[logging.Logger] = None) -> None:
        self.config = config
        self.logger = logger or LOGGER
        self.validator = DatasetValidator(logger=self.logger)
        self._register_signal_handlers()

    def _register_signal_handlers(self) -> None:
        signal.signal(signal.SIGINT, self._handle_termination)
        signal.signal(signal.SIGTERM, self._handle_termination)

    def _handle_termination(self, signum: int, frame: Any) -> None:
        self.logger.warning(f"Termination signal received (Signal: {signum}). Cleaning up resources...")
        sys.exit(128 + signum)

    def execute(self) -> Dict[str, Any]:
        self.logger.info("=" * 70)
        self.logger.info("STARTING QWEN 2.5 1.5B FINE-TUNING PIPELINE (APPLE SILICON)")
        self.logger.info("=" * 70)

        self.logger.info("Step 1/4: Validating input datasets...")
        train_rows = self.validator.validate_file(self.config.train_path)
        valid_rows = self.validator.validate_file(self.config.valid_path)
        self.logger.info(f"Dataset integrity verified: {train_rows} train rows, {valid_rows} validation rows.")

        self.logger.info("Step 2/4: Persisting configuration metadata...")
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        config_path = output_dir / "training_config.json"
        self.config.save_json(config_path)
        self.logger.info(f"Configuration metadata saved to: {config_path}")

        self.logger.info(f"Step 3/4: Initializing trainer with backend: {self.config.backend.upper()}")
        trainer: ModelTrainer
        if self.config.backend.lower() == "mlx":
            trainer = MLXModelTrainer(config=self.config, logger=self.logger)
        elif self.config.backend.lower() in ("torch", "mps", "pytorch"):
            trainer = PyTorchMPSModelTrainer(config=self.config, logger=self.logger)
        else:
            raise ValueError(f"Unsupported backend: {self.config.backend}. Supported: 'mlx', 'torch'")

        self.logger.info("Step 4/4: Executing parameter-efficient training...")
        metrics = trainer.train()

        summary_path = output_dir / "training_summary.json"
        summary_data = {
            "config": self.config.to_dict(),
            "metrics": metrics,
            "train_rows": train_rows,
            "valid_rows": valid_rows,
        }
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_data, f, indent=2)

        self.logger.info(f"Training summary saved to: {summary_path}")
        self.logger.info("=" * 70)
        self.logger.info("FINE-TUNING PIPELINE COMPLETED SUCCESSFULLY")
        self.logger.info("=" * 70)

        return summary_data
