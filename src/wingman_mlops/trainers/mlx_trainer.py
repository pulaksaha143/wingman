from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict

from src.wingman_mlops.config import FineTuningConfig
from src.wingman_mlops.exceptions import HardwareConfigurationError, TrainingExecutionError
from src.wingman_mlops.trainers.base import ModelTrainer


class MLXModelTrainer(ModelTrainer):
    def train(self) -> Dict[str, Any]:
        self.logger.info("Verifying MLX framework environment on Apple Silicon...")
        try:
            import mlx.core as mx
            import mlx_lm
        except ImportError as exc:
            error_msg = "MLX or MLX-LM is not installed. Install via: pip install mlx mlx-lm"
            self.logger.error(error_msg)
            raise HardwareConfigurationError(error_msg) from exc

        self.logger.info(f"MLX version: {mx.__version__} | Target Device: Apple Silicon GPU / Unified Memory")
        self.logger.info(f"Base model path: {self.config.model_path}")

        adapter_path = self.output_dir / "adapters"
        adapter_path.mkdir(parents=True, exist_ok=True)

        data_dir = Path(self.config.train_path).parent.resolve()
        
        self.logger.info("Configured MLX-LM LoRA parameters:")
        self.logger.info(f"  Model: {self.config.model_path}")
        self.logger.info(f"  Batch size: {self.config.batch_size}")
        self.logger.info(f"  LoRA rank: {self.config.lora_rank}")
        self.logger.info(f"  LoRA alpha: {self.config.lora_alpha}")
        self.logger.info(f"  LoRA layers: {self.config.lora_layers}")
        self.logger.info(f"  Learning rate: {self.config.learning_rate}")
        self.logger.info(f"  Max sequence length: {self.config.max_seq_length}")

        with open(self.config.train_path, "r", encoding="utf-8") as f:
            train_rows = sum(1 for _ in f)
            
        samples_per_step = self.config.batch_size * self.config.gradient_accumulation_steps
        steps_per_epoch = max(1, train_rows // samples_per_step)
        total_iters = self.config.num_epochs * steps_per_epoch
        
        self.logger.info(f"Dynamic Iteration Calculation: {train_rows} rows / {samples_per_step} samples per step = {steps_per_epoch} steps/epoch. Total iters: {total_iters}")

        start_time = time.time()
        
        try:
            cmd = [
                sys.executable, "-m", "mlx_lm", "lora",
                "--model", str(self.config.model_path),
                "--train",
                "--data", str(data_dir),
                "--adapter-path", str(adapter_path),
                "--batch-size", str(self.config.batch_size),
                "--num-layers", str(self.config.lora_layers),
                "--grad-accumulation-steps", str(self.config.gradient_accumulation_steps),
                "--learning-rate", str(self.config.learning_rate),
                "--iters", str(total_iters),
                "--steps-per-report", str(self.config.eval_steps),
                "--steps-per-eval", str(self.config.eval_steps),
                "--save-every", str(self.config.save_steps),
                "--max-seq-length", str(self.config.max_seq_length),
                "--seed", str(self.config.seed)
            ]
            
            self.logger.info(f"Launching MLX subprocess: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            
            duration = time.time() - start_time
            self.logger.info(f"MLX fine-tuning completed successfully in {duration:.2f} seconds.")

            return {
                "status": "completed",
                "backend": "mlx",
                "duration_seconds": round(duration, 2),
                "adapter_path": str(adapter_path),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except subprocess.CalledProcessError as exc:
            error_msg = f"MLX training process returned non-zero exit code: {exc.returncode}"
            self.logger.error(error_msg)
            raise TrainingExecutionError(error_msg) from exc
        except Exception as exc:
            error_msg = f"Unexpected error during MLX training: {str(exc)}"
            self.logger.error(error_msg)
            raise TrainingExecutionError(error_msg) from exc
