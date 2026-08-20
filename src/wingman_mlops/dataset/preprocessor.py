from __future__ import annotations

from typing import Optional


class ChatMLPreprocessor:
    def __init__(self, system_prompt: Optional[str] = None) -> None:
        self.system_prompt = system_prompt or (
            "You are a witty, chronically online Gen Z wingman and roast AI model. "
            "Deliver sharp, deadpan feedback and elite banter with zero corporate filler."
        )

    def format_pair(self, prompt: str, completion: str) -> str:
        return (
            "<|im_start|>system\n"
            f"{self.system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt.strip()}<|im_end|>\n"
            f"<|im_start|>assistant\n{completion.strip()}<|im_end|>\n"
        )

    def format_inference_prompt(self, prompt: str) -> str:
        return (
            "<|im_start|>system\n"
            f"{self.system_prompt}<|im_end|>\n"
            f"<|im_start|>user\n{prompt.strip()}<|im_end|>\n"
            "<|im_start|>assistant\n"
        )
