import os
from huggingface_hub import snapshot_download

model_id = "Qwen/Qwen2.5-1.5B"
local_dir = "models/Qwen2.5-1.5B"

os.makedirs(local_dir, exist_ok=True)

snapshot_download(
    repo_id=model_id,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    resume_download=True
)
