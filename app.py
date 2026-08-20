import os
import re
import sys
from pathlib import Path
import gradio as gr

sys.path.insert(0, str(Path(__file__).parent.resolve()))

CUSTOM_CSS = """
/* ── Global dark base ── */
body, gradio-app {
    background: #121212 !important;
    color: #e0e0e0 !important;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
}

.gradio-container {
    max-width: 800px !important;
    margin: 0 auto !important;
    padding: 20px 16px !important;
}

/* Hide Gradio footer */
footer { display: none !important; }

/* ── Header ── */
.header {
    text-align: center;
    margin-bottom: 24px;
}
.header h1 {
    font-size: 28px;
    font-weight: 700;
    color: #e0e0e0;
    margin: 0;
}
.header p {
    font-size: 16px;
    color: #8a8a8a;
    margin: 4px 0 0;
}

/* ── Chatbot ── */
#wingman-chatbot {
    background: #1a1a1a !important;
    border-radius: 12px !important;
    padding: 16px !important;
    border: 1px solid #2a2a2a !important;
    margin-bottom: 16px !important;
}
#wingman-chatbot .message {
    margin: 8px 0 !important;
    padding: 12px 16px !important;
    border-radius: 12px !important;
    width: fit-content !important;
    max-width: 85% !important;
    word-break: break-word !important;
    white-space: pre-wrap !important;
}
#wingman-chatbot .message.user,
#wingman-chatbot [data-testid="user"] {
    background: #0a6b7c !important;
    color: #ffffff !important;
    align-self: flex-end !important;
    margin-left: auto !important;
    border-bottom-right-radius: 4px !important;
    width: fit-content !important;
}
#wingman-chatbot .message.bot,
#wingman-chatbot [data-testid="bot"] {
    background: #2a2a2a !important;
    color: #e0e0e0 !important;
    border: 1px solid #3a3a3a !important;
    align-self: flex-start !important;
    margin-right: auto !important;
    border-bottom-left-radius: 4px !important;
    width: fit-content !important;
}
#wingman-chatbot .avatar-container {
    display: none !important;
}

/* ── Input row ── */
#input-row {
    display: flex !important;
    gap: 12px !important;
    align-items: flex-end !important;
    background: transparent !important;
}

/* Textbox – dark, pill‑shaped, auto‑expand */
#wingman-input textarea {
    background: #1e1e1e !important;
    color: #e0e0e0 !important;
    border: 2px solid #0a6b7c !important;
    border-radius: 24px !important;
    padding: 14px 18px !important;
    font-size: 15px !important;
    line-height: 1.5 !important;
    min-height: 80px !important;
    height: auto !important;
    resize: none !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.3) !important;
}
#wingman-input textarea:focus {
    border-color: #0e8b9e !important;
    outline: none !important;
}
#wingman-input textarea::placeholder {
    color: #8a8a8a !important;
}

/* Buttons – pill‑shaped, dark */
.action-btn {
    background: #2a2a2a !important;
    color: #e0e0e0 !important;
    border: 1px solid #3a3a3a !important;
    border-radius: 24px !important;
    padding: 12px 20px !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    cursor: pointer !important;
    transition: all 0.2s !important;
    min-height: 48px !important;
    white-space: nowrap !important;
}
.action-btn:hover {
    background: #3a3a3a !important;
    border-color: #4a4a4a !important;
}
#send-btn {
    background: #0a6b7c !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 24px !important;
    padding: 12px 24px !important;
    font-weight: 700 !important;
    font-size: 15px !important;
    box-shadow: 0 4px 12px rgba(10, 107, 124, 0.4) !important;
    min-height: 48px !important;
}
#send-btn:hover {
    background: #0e8b9e !important;
    box-shadow: 0 6px 16px rgba(10, 107, 124, 0.6) !important;
}
#clear-btn {
    background: transparent !important;
    border: 1px solid #3a3a3a !important;
    color: #b0b0b0 !important;
}
#clear-btn:hover {
    background: #2a2a2a !important;
    color: #ffffff !important;
}

/* ── Custom output styles ── */
.aura-score-badge {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    padding: 3px 8px;
    border-radius: 12px;
    margin-bottom: 8px;
}
.aura-score-pos { background-color: #1e4a3b; color: #8fe0c0; border: 1px solid #2a6b55; }
.aura-score-neg { background-color: #4a2a2a; color: #f0a0a0; border: 1px solid #6b3a3a; }
.verdict-text { font-weight: 700; color: #8fe0c0; margin-bottom: 6px; }
.roast-text { color: #e0e0e0; font-size: 15px; line-height: 1.6; }
.diagnosis-text {
    color: #f0a0a0; font-weight: 700; font-size: 13px;
    text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px;
}
.option-item {
    margin-top: 8px; padding: 10px 14px; background-color: #1e1e1e;
    border: 1px solid #3a3a3a; border-left: 3px solid #0a6b7c;
    border-radius: 0 10px 10px 0; font-size: 14px; line-height: 1.5;
}
.option-item strong {
    color: #8fe0c0; display: block; font-size: 12px;
    text-transform: uppercase; margin-bottom: 3px;
}
"""

def get_model(model_path: str, adapter_path: str | None, gguf_path: str):
    # Force GGUF backend to perfectly simulate Hugging Face Spaces
    USE_MLX = False

    if USE_MLX:
        if adapter_path and os.path.exists(adapter_path):
            model, tokenizer = mlx_lm.load(model_path, adapter_path=adapter_path)
        else:
            model, tokenizer = mlx_lm.load(model_path)
        try:
            im_end_id = tokenizer.encode("<|im_end|>")[0]
            if hasattr(tokenizer, "eos_token_ids"):
                tokenizer.eos_token_ids.add(im_end_id)
        except Exception:
            pass
        return {"type": "mlx", "model": model, "tokenizer": tokenizer}
    else:
        from llama_cpp import Llama
        if not os.path.exists(gguf_path):
            raise FileNotFoundError(f"GGUF model not found at {gguf_path}.")
        llm = Llama(model_path=gguf_path, n_ctx=2048, verbose=False)
        return {"type": "llama", "model": llm, "tokenizer": None}

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
        if stripped.startswith("Roast:") and ("Rating:" in "\n".join(cleaned_lines) or "Aura:" in "\n".join(cleaned_lines) or "Verdict:" in "\n".join(cleaned_lines)):
            break
        if (stripped.startswith("Option 2") or "Option 2 (" in stripped) and "Diagnosis:" in "\n".join(cleaned_lines):
            break
        if (stripped.startswith("Option 3") or "Option 3 (" in stripped) and "Option 1" in "\n".join(cleaned_lines):
            break
    return "\n".join(cleaned_lines).strip()

def generate_chat_response(model_bundle, prompt_str: str, max_tokens: int, temp: float) -> str:
    messages = [{"role": "user", "content": prompt_str.strip()}]
    
    if model_bundle["type"] == "mlx":
        import mlx.core as mx
        import mlx_lm
        from mlx_lm.sample_utils import make_sampler
        
        model = model_bundle["model"]
        tokenizer = model_bundle["tokenizer"]
        formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
        sampler = make_sampler(temp=temp)
        
        gpu_stream = mx.default_stream(mx.gpu)
        with mx.stream(gpu_stream):
            raw_response = mlx_lm.generate(
                model, tokenizer, prompt=formatted_prompt,
                max_tokens=max_tokens, sampler=sampler, verbose=False
            )
    else:
        llm = model_bundle["model"]
        response = llm.create_chat_completion(
            messages=messages, max_tokens=max_tokens, temperature=temp, stream=False,
            stop=["<|im_end|>", "<|endoftext|>"], repeat_penalty=1.15
        )
        raw_response = response['choices'][0]['message']['content']
    
    return clean_response(raw_response)

model_path = "models/Qwen2.5-1.5B"
gguf_path = "models/wingman.gguf"
active_adapter = (
    "outputs/qwen2.5-1.5b-wingman-lora/adapters"
    if os.path.exists("outputs/qwen2.5-1.5b-wingman-lora/adapters")
    else "outputs/smoke-test/adapters"
)
temperature = 0.7
max_tokens = 256

try:
    global_model_bundle = get_model(model_path, active_adapter, gguf_path)
except Exception as e:
    global_model_bundle = None
    print(f"Failed to load model: {e}")


def format_response(text: str) -> str:
    if "Rating:" in text or "Aura:" in text or "Verdict:" in text:
        score_val = "0/10"
        score_label = "RATING"
        verdict_val = ""
        roast_val = text
        for line in text.split("\n"):
            if line.startswith("Aura:"):
                score_val = line.replace("Aura:", "").strip()
                score_label = "AURA"
            elif line.startswith("Rating:"):
                score_val = line.replace("Rating:", "").strip()
                score_label = "RATING"
            elif line.startswith("Verdict:"):
                verdict_val = line.replace("Verdict:", "").strip()
            elif line.startswith("Roast:"):
                roast_val = line.replace("Roast:", "").strip()
        is_pos = False
        if score_label == "AURA":
            is_pos = "+" in score_val or ("-" not in score_val and score_val != "0")
        else:
            try:
                rating_num = float(score_val.split("/")[0])
                is_pos = rating_num >= 6.0
            except:
                is_pos = False
        badge_class = "aura-score-pos" if is_pos else "aura-score-neg"
        verdict_span = f'<span class="verdict-text" style="margin-left: 8px;">{verdict_val}</span>' if verdict_val else ''
        return f'<div><span class="aura-score-badge {badge_class}">{score_label}: {score_val}</span>{verdict_span}</div><div class="roast-text">{roast_val}</div>'

    elif "Diagnosis:" in text or "Option 1" in text:
        diag_val = ""
        options = []
        curr_opt_idx = -1
        for line in text.split("\n"):
            if line.startswith("Diagnosis:"):
                diag_val = line.replace("Diagnosis:", "").strip()
                curr_opt_idx = -1
            elif line.startswith("Option"):
                parts = line.split(":", 1)
                t = parts[0].strip()
                b = parts[1].strip() if len(parts) > 1 else ""
                options.append([t, b])
                curr_opt_idx = len(options) - 1
            elif curr_opt_idx != -1 and line.strip():
                options[curr_opt_idx][1] += " " + line.strip()
        if not diag_val and not options:
            return text
        else:
            diag_html = f'<div class="diagnosis-text">DIAGNOSIS: {diag_val}</div>' if diag_val else ''
            opts_html = "".join([f'<div class="option-item"><strong>{t}</strong> {b}</div>' for t, b in options])
            return f'{diag_html}{opts_html}'
    else:
        return text

def respond(user_message, chat_history):
    input_text = user_message.strip()
    lower_input = input_text.lower()
    curr_mode = None
    target_to_process = None

    if lower_input.startswith("/judge "):
        curr_mode = "JUDGE"
        target_to_process = input_text[7:].strip()
    elif lower_input.startswith("/refine "):
        curr_mode = "REFINE"
        target_to_process = input_text[8:].strip()
    elif lower_input.startswith("/gen "):
        curr_mode = "GENERATE"
        target_to_process = input_text[5:].strip()
    elif lower_input.startswith("/generate "):
        curr_mode = "GENERATE"
        target_to_process = input_text[10:].strip()

    if not target_to_process:
        guide_message = (
            "**Oops! Please use a command to tell Wingman what to do.**\n\n"
            "• `/judge [text]` — Rate a pickup line or message\n"
            "• `/refine [text]` — Polish your draft\n"
            "• `/gen [scenario]` — Generate openers or ideas"
        )
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": guide_message})
        return "", chat_history

    if curr_mode == "JUDGE":
        full_prompt = f"[JUDGE] Line: '{target_to_process}'"
    elif curr_mode == "REFINE":
        full_prompt = f"[REFINE] Line: '{target_to_process}'"
    else:
        if not target_to_process.lower().startswith("scenario:"):
            full_prompt = f"[GENERATE] Scenario: {target_to_process}"
        else:
            full_prompt = f"[GENERATE] {target_to_process}"

    try:
        if global_model_bundle is None:
            raise Exception("Model not loaded properly.")
        reply = generate_chat_response(global_model_bundle, full_prompt, max_tokens, temperature)
        formatted_reply = format_response(reply)
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": formatted_reply})
    except Exception as e:
        chat_history.append({"role": "user", "content": user_message})
        chat_history.append({"role": "assistant", "content": f"Execution error: {str(e)}"})

    return "", chat_history

def clear_chat():
    return []


with gr.Blocks(title="Wingman") as demo:
    # Header
    gr.HTML("""
        <div class="header">
            <h1>Wingman</h1>
        </div>
    """)

    # Chatbot
    chatbot = gr.Chatbot(
        elem_id="wingman-chatbot",
        label=None,
        height=450
    )

    # Input row: textbox + action buttons
    with gr.Row(elem_id="input-row"):
        msg = gr.Textbox(
            placeholder="Use /judge, /refine, or /gen followed by your text...",
            show_label=False,
            container=False,
            elem_id="wingman-input",
            lines=2
        )
        with gr.Column(scale=0, min_width=120):
            send_btn = gr.Button("Submit", elem_id="send-btn", variant="primary")
            
    with gr.Row():
        clear_btn = gr.Button("Clear Chat", elem_id="clear-btn", variant="secondary")

    # Wire up events
    send_btn.click(respond, [msg, chatbot], [msg, chatbot])
    msg.submit(respond, [msg, chatbot], [msg, chatbot])
    clear_btn.click(clear_chat, [], [chatbot])

if __name__ == "__main__":
    demo.launch(
        server_name="0.0.0.0",
        server_port=7860,
        css=CUSTOM_CSS
    )