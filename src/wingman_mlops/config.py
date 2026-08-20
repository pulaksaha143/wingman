from __future__ import annotations

import dataclasses
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict


@dataclass
class FineTuningConfig:
    model_path: str = "models/Qwen2.5-1.5B"
    train_path: str = "train.jsonl"
    valid_path: str = "valid.jsonl"
    output_dir: str = "outputs/qwen2.5-1.5b-wingman-lora"
    
    backend: str = "mlx"
    
    batch_size: int = 4
    gradient_accumulation_steps: int = 4
    learning_rate: float = 1e-4
    num_epochs: int = 3
    max_seq_length: int = 1024
    
    lora_rank: int = 8
    lora_alpha: float = 16.0
    lora_dropout: float = 0.05
    lora_layers: int = 16
    
    eval_steps: int = 25
    save_steps: int = 50
    seed: int = 42
    
    system_prompt: str = (
        "You are a witty, chronically online Gen Z wingman and roast AI model. "
        "Deliver sharp, deadpan feedback and elite banter with zero corporate filler."
    )
    
    extra_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    def save_json(self, destination: str | Path) -> None:
        dest_path = Path(destination)
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        with open(dest_path, "w", encoding="utf-8") as handle:
            json.dump(self.to_dict(), handle, indent=2)

    @classmethod
    def from_json(cls, source: str | Path) -> FineTuningConfig:
        with open(source, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        return cls(**data)
