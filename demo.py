from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.resolve()))

from src.wingman_mlops.logger import LOGGER


import re


def clean_response(text: str) -> str:
    if "<|im_end|>" in text:
        text = text.split("<|im_end|>")[0]

    lines = text.strip().split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("!") or stripped.startswith("[") or "!" in stripped[:5]:
            break

        stripped = re.sub(r"[^\x00-\x7F]+", "", stripped).strip()
        if not stripped:
            continue

        cleaned_lines.append(stripped)

        if stripped.startswith("Roast:") and ("Aura:" in "\n".join(cleaned_lines) or "Verdict:" in "\n".join(cleaned_lines)):
            break
        if (stripped.startswith("Option 2") or "Option 2 (" in stripped) and "Diagnosis:" in "\n".join(cleaned_lines):
            break
        if (stripped.startswith("Option 3") or "Option 3 (" in stripped) and "Option 1" in "\n".join(cleaned_lines):
            break

    return "\n".join(cleaned_lines).strip()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run inference on base or fine-tuned Qwen 2.5 1.5B model.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    parser.add_argument("--model-path", type=str, default="models/Qwen2.5-1.5B", help="Path to base model directory.")
    parser.add_argument("--adapter-path", type=str, default=None, help="Path to fine-tuned LoRA adapters (optional).")
    parser.add_argument("--prompt", type=str, default=None, help="Single prompt string to evaluate.")
    parser.add_argument("--max-tokens", type=int, default=256, help="Maximum new tokens to generate.")
    parser.add_argument("--temp", type=float, default=0.7, help="Sampling temperature.")
    parser.add_argument("--backend", type=str, choices=["mlx", "torch"], default="mlx", help="Inference backend.")
    return parser.parse_args()


def run_mlx_inference(model_path: str, adapter_path: str | None, prompt: str, max_tokens: int, temp: float) -> str:
    import mlx_lm
    from mlx_lm.sample_utils import make_sampler

    LOGGER.info(f"Loading MLX model from: {model_path}")
    if adapter_path and Path(adapter_path).exists():
        LOGGER.info(f"Applying LoRA adapter from: {adapter_path}")
        model, tokenizer = mlx_lm.load(model_path, adapter_path=adapter_path)
    else:
        model, tokenizer = mlx_lm.load(model_path)

    try:
        im_end_id = tokenizer.encode("<|im_end|>")[0]
        if hasattr(tokenizer, "eos_token_ids"):
            tokenizer.eos_token_ids.add(im_end_id)
    except Exception:
        pass

    messages = [{"role": "user", "content": prompt.strip()}]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    sampler = make_sampler(temp=temp)

    LOGGER.info("Generating response...")
    response = mlx_lm.generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False
    )
    return clean_response(response)


def run_torch_inference(model_path: str, adapter_path: str | None, prompt: str, max_tokens: int, temp: float) -> str:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    from peft import PeftModel

    device = torch.device("mps" if torch.backends.mps.is_available() else "cpu")
    LOGGER.info(f"Loading PyTorch model on device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_path,
        torch_dtype=torch.bfloat16,
        trust_remote_code=True
    ).to(device)

    if adapter_path and Path(adapter_path).exists():
        LOGGER.info(f"Loading PEFT adapter from: {adapter_path}")
        model = PeftModel.from_pretrained(model, adapter_path).to(device)

    messages = [{"role": "user", "content": prompt.strip()}]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    inputs = tokenizer(formatted_prompt, return_tensors="pt").to(device)

    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=max_tokens,
            temperature=temp,
            do_sample=temp > 0.0,
            pad_token_id=tokenizer.eos_token_id
        )

    generated_text = tokenizer.decode(outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True)
    return clean_response(generated_text)


def main() -> None:
    args = parse_args()

    sample_prompts = [
        "[JUDGE] Line: 'Are you a magician? Because whenever I look at you, everyone else disappears.'",
        "[REFINE] Line: 'Hey what are your plans for the weekend?'",
        "[GENERATE] Scenario: Bio says 'Probably listening to deftones, obsessed with film cameras, and drinking black coffee at 2 AM.'"
    ]

    prompts_to_run = [args.prompt] if args.prompt else sample_prompts

    for p in prompts_to_run:
        LOGGER.info("-" * 60)
        LOGGER.info(f"INPUT PROMPT:\n{p}")
        LOGGER.info("-" * 60)

        if args.backend == "mlx":
            output = run_mlx_inference(args.model_path, args.adapter_path, p, args.max_tokens, args.temp)
        else:
            output = run_torch_inference(args.model_path, args.adapter_path, p, args.max_tokens, args.temp)

        LOGGER.info(f"MODEL RESPONSE:\n{output.strip()}")


if __name__ == "__main__":
    main()
