# MLOps Guide: Fine-Tuning Qwen 2.5 1.5B on Apple Silicon

This guide provides step-by-step instructions for dataset preparation, model fine-tuning with LoRA/QLoRA, evaluation, and smoke testing on Apple Silicon (M-Series) using MLX-LM and PyTorch MPS.

---

## 1. Environment Setup & Installation

### 1.1 Prerequisites
- macOS 13.0+ (Ventura, Sonoma, Sequoia)
- Apple Silicon Chip (M1 / M2 / M3 / M4 / Pro / Max / Ultra)
- Python 3.10+
- Git and Git LFS

### 1.2 Virtual Environment Configuration
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 2. Model & Dataset Preparation

### 2.1 Download Base Model
Download the official `Qwen/Qwen2.5-1.5B` repository locally:
```bash
python scripts/download_model.py
```
Model files will be saved in `models/Qwen2.5-1.5B/`.

### 2.2 Dataset Verification
Ensure `train.jsonl` (1,000 rows) and `valid.jsonl` (100 rows) are present and properly formatted:
```bash
python -c "
import json
for split in ['train.jsonl', 'valid.jsonl']:
    with open(split) as f:
        data = [json.loads(line) for line in f if line.strip()]
    print(f'{split}: {len(data)} valid records')
"
```

---

## 3. Fine-Tuning Execution Options

There are two primary ways to run fine-tuning:

### Option A: Using the Orchestrated Pipeline (`train.py`)
This option includes automatic schema validation, structured logging, configuration saving, and execution metadata persistence.

#### Command for Apple MLX-LM (Recommended):
```bash
python train.py \
  --model-path models/Qwen2.5-1.5B \
  --train-path train.jsonl \
  --valid-path valid.jsonl \
  --output-dir outputs/qwen2.5-1.5b-wingman-lora \
  --backend mlx \
  --batch-size 4 \
  --gradient-accumulation-steps 4 \
  --learning-rate 1e-4 \
  --num-epochs 3 \
  --max-seq-length 1024 \
  --lora-rank 8 \
  --lora-alpha 16.0 \
  --lora-dropout 0.05 \
  --lora-layers 16 \
  --eval-steps 25 \
  --save-steps 50
```

#### Command for PyTorch MPS / PEFT (Fallback):
```bash
python train.py \
  --model-path models/Qwen2.5-1.5B \
  --train-path train.jsonl \
  --valid-path valid.jsonl \
  --output-dir outputs/qwen2.5-1.5b-wingman-torch \
  --backend torch \
  --batch-size 2 \
  --gradient-accumulation-steps 8 \
  --learning-rate 2e-4 \
  --num-epochs 3
```

---

### Option B: Using Direct MLX-LM CLI (`python -m mlx_lm lora`)
For direct low-level MLX tuning without the orchestrator wrapper:

```bash
python -m mlx_lm lora \
  --model models/Qwen2.5-1.5B \
  --train \
  --data . \
  --adapter-path outputs/qwen2.5-1.5b-wingman-lora/adapters \
  --batch-size 4 \
  --num-layers 16 \
  --grad-accumulation-steps 4 \
  --learning-rate 1e-4 \
  --iters 750 \
  --steps-per-report 25 \
  --steps-per-eval 25 \
  --save-every 50 \
  --max-seq-length 1024 \
  --seed 42
```

---

## 4. Smoke Testing & Quick Verification

### 4.1 Fast 1-Epoch Smoke Test
Run a quick test to verify memory allocation and gradient updates:
```bash
python train.py \
  --model-path models/Qwen2.5-1.5B \
  --train-path train.jsonl \
  --valid-path valid.jsonl \
  --output-dir outputs/smoke-test \
  --backend mlx \
  --batch-size 2 \
  --num-epochs 1 \
  --eval-steps 5 \
  --save-steps 10
```

### 4.2 Verifying Output Artifacts
```bash
ls -la outputs/qwen2.5-1.5b-wingman-lora/
```
Expected output files:
- `adapters/` (LoRA adapter weights: `adapters.safetensors`, `adapter_config.json`)
- `training_config.json` (Serialized run configuration)
- `training_summary.json` (Loss metrics, duration, record counts)

---

## 5. Model Evaluation & Inference

### 5.1 Interactive Inference via `demo.py`
```bash
python demo.py \
  --model-path models/Qwen2.5-1.5B \
  --adapter-path outputs/qwen2.5-1.5b-wingman-lora/adapters \
  --backend mlx \
  --temp 0.7 \
  --max-tokens 256
```

### 5.2 Single Prompt Evaluation
```bash
python demo.py \
  --model-path models/Qwen2.5-1.5B \
  --adapter-path outputs/qwen2.5-1.5b-wingman-lora/adapters \
  --prompt "[JUDGE] Line: 'Are you a parking ticket? Because you have fine written all over you.'" \
  --backend mlx
```

### 5.3 Direct MLX-LM Generation CLI
```bash
python -m mlx_lm generate \
  --model models/Qwen2.5-1.5B \
  --adapter-path outputs/qwen2.5-1.5b-wingman-lora/adapters \
  --prompt "<|im_start|>user\n[REFINE] Line: 'hru'<|im_end|>\n<|im_start|>assistant\n" \
  --max-tokens 256
```

### 5.4 Streamlit Web Dashboard
Launch the interactive web UI:
```bash
streamlit run app.py
```

---

## 6. Architecture & File Structure

```
fine/
├── src/
│   └── wingman_mlops/
│       ├── __init__.py           # Package exports
│       ├── config.py             # FineTuningConfig dataclass
│       ├── exceptions.py         # Custom domain exceptions
│       ├── logger.py             # Structured logging setup
│       ├── dataset/
│       │   ├── __init__.py
│       │   ├── validator.py      # Line-by-line schema validator
│       │   └── preprocessor.py   # ChatML format converter
│       ├── trainers/
│       │   ├── __init__.py
│       │   ├── base.py           # Abstract ModelTrainer
│       │   ├── mlx_trainer.py    # Apple MLX-LM LoRA trainer
│       │   └── torch_trainer.py  # PyTorch MPS + PEFT trainer
│       └── pipeline.py           # TrainingPipelineOrchestrator
├── scripts/
│   ├── download_model.py         # Base model snapshot downloader
│   ├── build_full_dataset.py     # Dataset builder (1000 train, 100 valid)
│   └── generate_data.py          # Data generation utilities
├── models/
│   └── Qwen2.5-1.5B/             # Local base model weights
├── train.jsonl                   # 1,000 training examples
├── valid.jsonl                   # 100 validation examples
├── train.py                      # CLI training entry point
├── demo.py                       # CLI inference entry point
├── app.py                        # Streamlit interactive web dashboard
├── requirements.txt              # Python dependencies
└── guide.md                      # MLOps user guide
```

---

## 7. Troubleshooting & Memory Optimization

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| `unrecognized arguments: --lora-layers` | Modern `mlx_lm` syntax uses `--num-layers` | Handled automatically in `train.py`, or use `--num-layers 16` in raw CLI. |
| `Calling python -m mlx_lm.lora directly is deprecated` | CLI module path changed | Use `python -m mlx_lm lora` instead of `python -m mlx_lm.lora`. |
| `OutOfMemoryError` / Process killed | Unified Memory exhausted | Reduce `--batch-size` to 2 or 1, and increase `--gradient-accumulation-steps` to 8 or 16. |
| `HardwareConfigurationError` | Missing MLX or PyTorch MPS | Run `pip install -r requirements.txt` and ensure macOS version is 13.0+. |
| `DatasetValidationError` | Malformed JSON or missing keys | Verify `train.jsonl` syntax. Every row must have `prompt` and `completion` keys. |
| `FileNotFoundError: models/Qwen2.5-1.5B` | Model weights not downloaded | Run `python scripts/download_model.py` before starting training. |
