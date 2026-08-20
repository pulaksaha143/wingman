import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.wingman_mlops.config import FineTuningConfig
from src.wingman_mlops.exceptions import FineTuningError
from src.wingman_mlops.logger import LOGGER
from src.wingman_mlops.pipeline import TrainingPipelineOrchestrator


def parse_cli_args() -> FineTuningConfig:
    parser = argparse.ArgumentParser(
        description="Production-grade fine-tuning for Qwen 2.5 1.5B on Apple Silicon (M-Series).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("--model-path", type=str, default="models/Qwen2.5-1.5B", help="Path to base model directory.")
    parser.add_argument("--train-path", type=str, default="train.jsonl", help="Path to training dataset.")
    parser.add_argument("--valid-path", type=str, default="valid.jsonl", help="Path to validation dataset.")
    parser.add_argument("--output-dir", type=str, default="outputs/qwen2.5-1.5b-wingman-lora", help="Output directory for adapters and logs.")
    parser.add_argument("--backend", type=str, choices=["mlx", "torch"], default="mlx", help="Framework backend (mlx or torch).")
    parser.add_argument("--batch-size", type=int, default=4, help="Batch size per training step.")
    parser.add_argument("--gradient-accumulation-steps", type=int, default=4, help="Gradient accumulation steps.")
    parser.add_argument("--learning-rate", type=float, default=1e-4, help="Learning rate.")
    parser.add_argument("--num-epochs", type=int, default=3, help="Number of training epochs.")
    parser.add_argument("--max-seq-length", type=int, default=1024, help="Maximum sequence length.")
    parser.add_argument("--lora-rank", type=int, default=8, help="LoRA rank.")
    parser.add_argument("--lora-alpha", type=float, default=16.0, help="LoRA scaling factor.")
    parser.add_argument("--lora-dropout", type=float, default=0.05, help="LoRA dropout rate.")
    parser.add_argument("--lora-layers", type=int, default=16, help="Number of layers to adapt.")
    parser.add_argument("--eval-steps", type=int, default=25, help="Steps between validation evaluations.")
    parser.add_argument("--save-steps", type=int, default=50, help="Steps between checkpoint saves.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed.")

    args = parser.parse_args()

    return FineTuningConfig(
        model_path=args.model_path,
        train_path=args.train_path,
        valid_path=args.valid_path,
        output_dir=args.output_dir,
        backend=args.backend,
        batch_size=args.batch_size,
        gradient_accumulation_steps=args.gradient_accumulation_steps,
        learning_rate=args.learning_rate,
        num_epochs=args.num_epochs,
        max_seq_length=args.max_seq_length,
        lora_rank=args.lora_rank,
        lora_alpha=args.lora_alpha,
        lora_dropout=args.lora_dropout,
        lora_layers=args.lora_layers,
        eval_steps=args.eval_steps,
        save_steps=args.save_steps,
        seed=args.seed
    )


def main() -> None:
    try:
        config = parse_cli_args()
        orchestrator = TrainingPipelineOrchestrator(config=config)
        orchestrator.execute()
    except FineTuningError as exc:
        LOGGER.error(f"Pipeline execution aborted: {str(exc)}")
        sys.exit(1)
    except Exception as exc:
        LOGGER.exception(f"Fatal unhandled exception: {str(exc)}")
        sys.exit(2)


if __name__ == "__main__":
    main()
