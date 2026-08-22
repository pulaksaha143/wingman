import os
import subprocess
import sys
import json

def count_jsonl_rows(filepath: str) -> int:
    if not os.path.exists(filepath):
        return 0
    with open(filepath, "r", encoding="utf-8") as f:
        return sum(1 for line in f if line.strip())

def main():
    # Use the 4-bit quantized Llama 3.1 8B Instruct (Best for M2 Air 16GB)
    # We download it to a local folder so you have full control over the weights
    base_model = "models/Meta-Llama-3.1-8B-Instruct-4bit"
    
    if not os.path.exists(base_model):
        print(f"Base model not found at {base_model}. Auto-downloading from Hugging Face...")
        try:
            from huggingface_hub import snapshot_download
        except ImportError:
            print("Error: huggingface_hub is not installed. Please run: pip install huggingface_hub")
            sys.exit(1)
            
        os.makedirs("models", exist_ok=True)
        # Download the specific 4-bit MLX version
        snapshot_download(repo_id="mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", local_dir=base_model)
    
    data_dir = "experiment3"
    train_data = os.path.join(data_dir, "train.jsonl")
    valid_data = os.path.join(data_dir, "valid.jsonl")
    adapter_dir = os.path.join(data_dir, "outputs3/llama-3.1-8b-instruct-wingman-lora/adapters")
    os.makedirs(adapter_dir, exist_ok=True)

    # Check if valid.jsonl exists, if not, create a small one from train.jsonl
    # MLX requires a valid.jsonl for evaluation loss tracking during training
    if not os.path.exists(valid_data):
        print("valid.jsonl not found in experiment3. Creating one by splitting train.jsonl...")
        with open(train_data, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Take ~5% for validation
        split_idx = int(len(lines) * 0.95)
        train_lines = lines[:split_idx]
        valid_lines = lines[split_idx:]
        
        with open(train_data, 'w', encoding='utf-8') as f:
            f.writelines(train_lines)
        with open(valid_data, 'w', encoding='utf-8') as f:
            f.writelines(valid_lines)
        print(f"Split {len(train_lines)} rows for training and {len(valid_lines)} rows for validation.")

    num_samples = count_jsonl_rows(train_data)
    if num_samples == 0:
        print("Error: train.jsonl is empty or missing!")
        sys.exit(1)

    # Dynamically determine optimal training iterations based on dataset size
    # 1.0 to 1.5 epochs is ideal. 1 epoch of 11,000 rows is great.
    target_epochs = 1.0
    
    # We must restrict batch-size and max-seq-length to avoid OOM on 16GB M2 Air
    batch_size = 1       
    dynamic_iters = max(100, int((num_samples * target_epochs) / batch_size))

    eval_steps = max(50, dynamic_iters // 20)
    save_steps = max(100, dynamic_iters // 10)

    print("=" * 65)
    print("M2 Air Optimized MLX LoRA Fine-Tuning (experiment3)")
    print(f"• Base Model       : {base_model}")
    print(f"• Dataset Samples  : {num_samples} rows in {train_data}")
    print(f"• Target Epochs    : {target_epochs}")
    print(f"• Batch Size       : {batch_size} (Memory Safe)")
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
        "--data", data_dir,
        "--adapter-path", adapter_dir,
        "--iters", str(dynamic_iters),
        "--batch-size", str(batch_size),
        "--num-layers", "16",
        "--learning-rate", "1e-4",
        "--steps-per-report", "20",
        "--steps-per-eval", str(eval_steps),
        "--save-every", str(save_steps),
        "--val-batches", "10",
        "--max-seq-length", "512"  # Strict cap to prevent massive RAM usage
    ]

    print("Running command with Overnight Thermal Throttle (50% Duty Cycle)...")
    print("Command:", " ".join(cmd))
    
    import time
    import signal
    
    proc = subprocess.Popen(cmd)
    try:
        while proc.poll() is None:
            # Let it train and heat up for 2 seconds
            time.sleep(2)
            if proc.poll() is not None:
                break
            
            # Pause the MLX process to let the GPU instantly cool down
            proc.send_signal(signal.SIGSTOP)
            time.sleep(2) # Cool down for 2 seconds
            
            # Resume training
            proc.send_signal(signal.SIGCONT)
            
    except KeyboardInterrupt:
        # If user hits Ctrl+C, ensure we unpause it before terminating so it doesn't leave a zombie
        proc.send_signal(signal.SIGCONT)
        proc.terminate()
        sys.exit(1)

    if proc.returncode != 0:
        print("Training failed with exit code:", proc.returncode)
        sys.exit(proc.returncode)

    print("=" * 65)
    print("Dynamic training complete! Adapters saved to:", adapter_dir)
    print("=" * 65)

if __name__ == "__main__":
    main()
