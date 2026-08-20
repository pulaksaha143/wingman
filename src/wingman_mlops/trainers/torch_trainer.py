from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Dict, List

from src.wingman_mlops.config import FineTuningConfig
from src.wingman_mlops.exceptions import HardwareConfigurationError, TrainingExecutionError
from src.wingman_mlops.trainers.base import ModelTrainer


class PyTorchMPSModelTrainer(ModelTrainer):
    def train(self) -> Dict[str, Any]:
        self.logger.info("Verifying PyTorch MPS hardware acceleration on Apple Silicon...")
        try:
            import torch
            import transformers
            from transformers import (
                AutoModelForCausalLM,
                AutoTokenizer,
                DataCollatorForSeq2Seq,
                Trainer,
                TrainingArguments,
            )
            from peft import LoraConfig, get_peft_model, TaskType
            from datasets import load_dataset
        except ImportError as exc:
            error_msg = "PyTorch, Transformers, or PEFT is missing. Install via requirements.txt"
            self.logger.error(error_msg)
            raise HardwareConfigurationError(error_msg) from exc

        if not torch.backends.mps.is_available():
            error_msg = "Apple Silicon MPS backend is not available on this system."
            self.logger.error(error_msg)
            raise HardwareConfigurationError(error_msg)

        device = torch.device("mps")
        self.logger.info(f"PyTorch version: {torch.__version__} | Target Device: {device}")

        start_time = time.time()
        adapter_output = self.output_dir / "peft_adapters"
        adapter_output.mkdir(parents=True, exist_ok=True)

        try:
            self.logger.info(f"Loading tokenizer from: {self.config.model_path}")
            tokenizer = AutoTokenizer.from_pretrained(
                self.config.model_path,
                trust_remote_code=True,
                padding_side="right"
            )
            if tokenizer.pad_token is None:
                tokenizer.pad_token = tokenizer.eos_token

            self.logger.info(f"Loading base model in bfloat16 for MPS from: {self.config.model_path}")
            model = AutoModelForCausalLM.from_pretrained(
                self.config.model_path,
                torch_dtype=torch.bfloat16,
                trust_remote_code=True
            )

            lora_config = LoraConfig(
                task_type=TaskType.CAUSAL_LM,
                r=self.config.lora_rank,
                lora_alpha=self.config.lora_alpha,
                lora_dropout=self.config.lora_dropout,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
                bias="none"
            )

            self.logger.info("Applying LoRA adapter configuration...")
            model = get_peft_model(model, lora_config)
            model.print_trainable_parameters()

            self.logger.info(f"Loading datasets: train={self.config.train_path}, valid={self.config.valid_path}")
            dataset = load_dataset(
                "json",
                data_files={
                    "train": self.config.train_path,
                    "validation": self.config.valid_path
                }
            )

            system_prompt = self.config.system_prompt

            def preprocess_function(examples: Dict[str, List[str]]) -> Dict[str, Any]:
                texts = [
                    f"<|im_start|>system\n{system_prompt}<|im_end|>\n"
                    f"<|im_start|>user\n{p}<|im_end|>\n"
                    f"<|im_start|>assistant\n{c}<|im_end|>"
                    for p, c in zip(examples["prompt"], examples["completion"])
                ]
                return tokenizer(
                    texts,
                    truncation=True,
                    max_length=self.config.max_seq_length,
                    padding=False
                )

            self.logger.info("Tokenizing datasets with ChatML template...")
            tokenized_dataset = dataset.map(
                preprocess_function,
                batched=True,
                remove_columns=["prompt", "completion"]
            )

            training_args = TrainingArguments(
                output_dir=str(self.output_dir / "checkpoints"),
                per_device_train_batch_size=self.config.batch_size,
                per_device_eval_batch_size=self.config.batch_size,
                gradient_accumulation_steps=self.config.gradient_accumulation_steps,
                learning_rate=self.config.learning_rate,
                num_train_epochs=self.config.num_epochs,
                logging_steps=self.config.eval_steps,
                eval_strategy="steps",
                eval_steps=self.config.eval_steps,
                save_strategy="steps",
                save_steps=self.config.save_steps,
                save_total_limit=2,
                bf16=False,
                report_to="none",
                use_mps_device=True,
                seed=self.config.seed
            )

            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=tokenized_dataset["train"],
                eval_dataset=tokenized_dataset["validation"],
                data_collator=DataCollatorForSeq2Seq(tokenizer, pad_to_multiple_of=8, return_tensors="pt"),
            )

            self.logger.info("Executing PyTorch MPS training loop...")
            train_result = trainer.train()

            self.logger.info("Saving LoRA adapter weights and tokenizer artifacts...")
            model.save_pretrained(str(adapter_output))
            tokenizer.save_pretrained(str(adapter_output))

            duration = time.time() - start_time
            self.logger.info(f"PyTorch fine-tuning completed in {duration:.2f} seconds.")

            return {
                "status": "completed",
                "backend": "torch_mps",
                "train_loss": train_result.training_loss,
                "duration_seconds": round(duration, 2),
                "adapter_path": str(adapter_output),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
            }

        except Exception as exc:
            error_msg = f"PyTorch MPS training execution failed: {str(exc)}"
            self.logger.error(error_msg)
            raise TrainingExecutionError(error_msg) from exc
