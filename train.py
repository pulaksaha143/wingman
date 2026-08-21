import os
import subprocess
import sys

def count_jsonl_rows(filepath: str) -> int:
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

def main():
    base_model = "models/Qwen2.5-1.5B"
    if not os.path.exists(base_model):
        print(f"Base model not found at {base_model}. Downloading...")
        from huggingface_hub import snapshot_download
        os.makedirs("models", exist_ok=True)
        snapshot_download(repo_id="Qwen/Qwen2.5-1.5B", local_dir=base_model)

    train_data = "dataset/train.jsonl"
    adapter_dir = "outputs/qwen2.5-1.5b-wingman-lora/adapters"
    os.makedirs(adapter_dir, exist_ok=True)

    num_samples = count_jsonl_rows(train_data)
    if num_samples == 0:
        print("Error: train.jsonl is empty or missing!")
        sys.exit(1)

    # Dynamically determine optimal training iterations based on dataset size:
    # Standard LoRA fine-tuning sweet spot: 1.0 to 1.5 epochs
    target_epochs = 1.25
    batch_size = 4
    dynamic_iters = max(100, int((num_samples * target_epochs) / batch_size))
    # No hard cap, we want the model to see all the new diverse HuggingFace data!
    dynamic_iters = max(200, dynamic_iters)

    eval_steps = max(25, dynamic_iters // 10)
    save_steps = max(50, dynamic_iters // 5)

    print("=" * 65)
    print("Dynamic MLX LoRA Fine-Tuning on Apple Silicon")
    print(f"• Base Model       : {base_model}")
    print(f"• Dataset Samples  : {num_samples} rows in {train_data}")
    print(f"• Target Epochs    : {target_epochs}")
    print(f"• Batch Size       : {batch_size}")
    print(f"• Calculated Iters : {dynamic_iters} iterations (Dynamic)")
    print(f"• Output Path      : {adapter_dir}")
    print("=" * 65)

    cmd = [
        sys.executable,
        "-m",
        "mlx_lm",
        "lora",
        "--model", base_model,
        "--train",
        "--data", "dataset",
        "--adapter-path", adapter_dir,
        "--iters", str(dynamic_iters),
        "--batch-size", str(batch_size),
        "--num-layers", "16",
        "--learning-rate", "5e-5",
        "--mask-prompt",
        "--steps-per-report", "20",
        "--steps-per-eval", str(eval_steps),
        "--save-every", str(save_steps),
        "--val-batches", "15",
        "--max-seq-length", "1024"
    ]

    print("Running command:", " ".join(cmd))
    res = subprocess.run(cmd)
    if res.returncode != 0:
        print("Training failed with exit code:", res.returncode)
        sys.exit(res.returncode)

    print("=" * 65)
    print("Dynamic training complete! Adapters saved to:", adapter_dir)
    print("=" * 65)

if __name__ == "__main__":
    main()
