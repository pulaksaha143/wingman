import os
import re
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.resolve()))

# ─── STREAMLIT CONFIG ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Wingman (Experiment 3 - Llama 8B)",
    page_icon="🥂",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
    :root {
        --primary: #0e5f6e;
        --primary-hover: #0b4955;
        --bg-main: #f7f9fa;
        --text-main: #1a2a32;
        --text-muted: #8b9ea8;
        --border-light: #e5eaed;
    }

    * {
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
    }

    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--text-main) !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    .main .block-container {
        max-width: 760px !important;
        padding-top: 20px !important;
        padding-bottom: 120px !important; 
    }

    /* Header styling */
    .brand-group {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 24px;
    }

    .brand-name {
        font-size: 24px;
        font-weight: 700;
        color: var(--primary);
        margin: 0;
    }

    /* Chat Messages */
    .msg-row-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 16px;
        animation: fadeIn 0.25s ease forwards;
    }

    .msg-bubble-user {
        background-color: var(--primary);
        color: #ffffff;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        font-size: 15px;
        line-height: 1.5;
        word-wrap: break-word;
    }

    .msg-row-bot {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 16px;
        animation: fadeIn 0.25s ease forwards;
    }

    .msg-body-bot {
        background-color: #ffffff;
        color: var(--text-main);
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        border: 1px solid var(--border-light);
    }

    /* Bot Special Formats */
    .aura-score-badge {
        display: inline-block;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        padding: 3px 8px;
        border-radius: 6px;
        margin-bottom: 8px;
    }
    .aura-score-pos { background: #eef4f6; color: var(--primary); border: 1px solid #bce1e8; }
    .aura-score-neg { background: #FDE8E7; color: #B52A25; border: 1px solid #f8c1be; }

    .verdict-text { font-weight: 700; color: var(--primary); margin-bottom: 6px; }
    .roast-text { color: var(--text-main); font-size: 15px; line-height: 1.6; }

    .diagnosis-text {
        color: var(--primary);
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 8px;
    }

    .option-item {
        margin-top: 8px;
        padding: 10px 14px;
        background-color: #f7f9fa;
        border: 1px solid var(--border-light);
        border-left: 3px solid var(--primary);
        border-radius: 0 10px 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }

    .option-item strong {
        color: var(--primary);
        display: block;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 3px;
    }

    /* Loading state */
    .loading-container { display: flex; justify-content: flex-start; margin-bottom: 24px; }
    .loading-text {
        font-size: 14px; font-weight: 600; color: var(--primary);
        display: flex; align-items: center; gap: 8px; animation: pulse 1.5s infinite;
        padding: 8px 14px; background: #ffffff; border: 1px solid var(--border-light);
        border-radius: 18px 18px 18px 4px; box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    @keyframes pulse { 0% { opacity: 0.7; } 50% { opacity: 1; } 100% { opacity: 0.7; } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* Bottom container & Input Pill Styling */
    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div {
        background-color: var(--bg-main) !important;
        background: var(--bg-main) !important;
    }

    div[data-testid="stChatInputContainer"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    div[data-testid="stChatInput"] {
        border-radius: 28px !important;
        border: 2px solid var(--primary) !important;
        background-color: #ffffff !important;
        box-shadow: 0 4px 16px rgba(14, 95, 110, 0.08) !important;
    }

    div[data-testid="stChatInput"] > div {
        background-color: transparent !important;
        background: transparent !important;
    }

    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: var(--text-main) !important;
    }

    div[data-testid="stChatInput"] button {
        background-color: var(--primary) !important;
        color: #ffffff !important;
        border-radius: 50% !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: var(--primary-hover) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# Dynamically hide sidebar unless settings is open
if not st.session_state.get("show_settings", False):
    st.markdown("""
        <style>
            section[data-testid="stSidebar"] {
                display: none !important;
            }
        </style>
    """, unsafe_allow_html=True)

# ─── MODEL LOADING ──────────────────────────────────────────────────────
@st.cache_resource
def get_model(model_path: str, adapter_path: str | None):
    import mlx.core as mx
    import mlx_lm

    try:
        mx.set_default_device(mx.gpu)
    except Exception:
        pass

    if adapter_path and os.path.exists(adapter_path):
        model, tokenizer = mlx_lm.load(model_path, adapter_path=adapter_path)
    else:
        model, tokenizer = mlx_lm.load(model_path)

    try:
        im_end_id = tokenizer.encode("<|im_end|>")[0]
        if hasattr(tokenizer, "eos_token_ids"):
            tokenizer.eos_token_ids.add(im_end_id)
        
        # Llama 3.1 specific token mapping for safety
        llama_eos = tokenizer.encode("<|eot_id|>")
        if llama_eos:
            if hasattr(tokenizer, "eos_token_ids"):
                tokenizer.eos_token_ids.add(llama_eos[0])
    except Exception:
        pass

    return {"type": "mlx", "model": model, "tokenizer": tokenizer}


def clean_response(text: str) -> str:
    # Llama 3.1 end of turn token cleanup
    if "<|eot_id|>" in text:
        text = text.split("<|eot_id|>")[0]
    if "<|im_end|>" in text:
        text = text.split("<|im_end|>")[0]

    lines = text.strip().split("\n")
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue
        if stripped.startswith("!") or (stripped.startswith("[") and len(cleaned_lines) > 0):
            break

        stripped = re.sub(r"[^\x00-\x7F]+", "", stripped).strip()
        if not stripped:
            continue

        cleaned_lines.append(stripped)

    return "\n".join(cleaned_lines).strip()


def generate_chat_response(model_bundle, prompt_str: str, curr_mode: str, max_tokens: int, temp: float) -> str:
    import mlx.core as mx
    import mlx_lm
    from mlx_lm.sample_utils import make_sampler

    try:
        mx.set_default_device(mx.gpu)
    except Exception:
        pass

    if curr_mode == "JUDGE":
        system_instruction = (
            "You are Wingman, an elite AI dating assistant.\n"
            "Evaluate the provided line honestly and output strictly in this format:\n"
            "Rating: <score>/10\n"
            "Verdict: <short witty title>\n"
            "Roast: <If the line is bad/cliché, deliver a savage witty roast. If the line is good, give enthusiastic praise.>"
        )
    elif curr_mode == "REFINE":
        system_instruction = (
            "You are Wingman, an elite AI dating assistant.\n"
            "Diagnose why the original line failed and provide two upgraded options strictly in this format:\n"
            "Diagnosis: <short breakdown of why the original line failed>\n"
            "Option 1 (Playful Tease): '<line>'\n"
            "Option 2 (Direct / Bold): '<line>'"
        )
    else:
        system_instruction = (
            "You are Wingman, an elite AI dating assistant.\n"
            "Generate three distinct and confident openers strictly in this format:\n"
            "Option 1 (Playful Tease): '<line>'\n"
            "Option 2 (Curiosity Hook): '<line>'\n"
            "Option 3 (Direct / Bold): '<line>'"
        )

    messages = [
        {"role": "system", "content": system_instruction},
        {"role": "user", "content": prompt_str.strip()},
    ]

    model = model_bundle["model"]
    tokenizer = model_bundle["tokenizer"]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    import time
    mx.random.seed(int(time.time() * 1000))
    
    # Strict but Creative settings:
    # temp=0.7 keeps the ideas wild and funny
    # top_k=40 & min_p=0.1 strictly blocks the model from hallucinating or losing the format
    sampler = make_sampler(temp=temp, top_p=0.9, top_k=40, min_p=0.1)

    raw_response = mlx_lm.generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False,
    )

    return clean_response(raw_response)


# ─── CONFIGURATION & INITIALIZATION ─────────────────────────────────────
import os
import streamlit as st

local_model_path = "models/Meta-Llama-3.1-8B-Instruct-4bit"
if not os.path.exists(local_model_path):
    # This ensures the model is physically downloaded into the models/ folder
    # if you decide to run the app before training (which uses the base model).
    from huggingface_hub import snapshot_download
    print(f"Model not found at {local_model_path}. Downloading from Hugging Face...")
    os.makedirs("models", exist_ok=True)
    snapshot_download(repo_id="mlx-community/Meta-Llama-3.1-8B-Instruct-4bit", local_dir=local_model_path)

model_path = local_model_path
active_adapter = (
    "experiment3/outputs3/llama-3.1-8b-instruct-wingman-lora/adapters"
    if os.path.exists("experiment3/outputs3/llama-3.1-8b-instruct-wingman-lora/adapters")
    else None
)
temperature = 0.7
max_tokens = 256

if "messages" not in st.session_state:
    st.session_state["messages"] = []

# ─── HEADER & NAV ───────────────────────────────────────────────────────
col_brand, col_settings, col_new = st.columns([6, 1.5, 1.5])
with col_brand:
    st.markdown(
        '<div class="brand-group"><h1 class="brand-name">Wingman 3.0 (Llama 8B)</h1></div>',
        unsafe_allow_html=True,
    )
with col_settings:
    st.write("") 
    if st.button("Settings", use_container_width=True):
        st.session_state["show_settings"] = not st.session_state.get("show_settings", False)
        st.rerun()
with col_new:
    st.write("") 
    if st.button("New Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

if active_adapter:
    st.sidebar.success("Fine-Tuned Llama LoRA is Active!")
else:
    st.sidebar.warning(" No LoRA found. Using base Llama model.")

if st.sidebar.button("Reload AI Model (Clear Cache)", use_container_width=True):
    st.cache_resource.clear()
    st.sidebar.success("Model cache cleared! Next prompt will load fresh weights from disk.")

# ─── CHAT INPUT HANDLING ────────────────────────────────────────────────
user_input = st.chat_input("Use /judge, /refine, or /gen followed by your text...")

if user_input:
    input_text = user_input.strip()
    lower_input = input_text.lower()

    st.session_state["messages"].append({"role": "user", "content": input_text})

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

    if target_to_process:
        st.session_state["pending_target"] = target_to_process
        st.session_state["pending_mode"] = curr_mode
    else:
        guide_message = (
            "💀 **Bro forgot the manual.** You can't just throw raw words at me without a command and expect rizz.\n\n"
            "Use a command so I know what to do with your message:\n\n"
            "• `/judge [line]` — Get a rating, verdict & roast (or praise if you actually cooked)\n"
            "• `/refine [draft]` — Let me fix your catastrophic draft into high-tier openers\n"
            "• `/gen [bio / situation]` — Cook up fresh, targeted openers from scratch"
        )
        st.session_state["messages"].append({"role": "assistant", "content": guide_message})
        st.rerun()

# ─── RENDER CHAT HISTORY ────────────────────────────────────────────────
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="msg-row-user"><div class="msg-bubble-user">{msg["content"]}</div></div>',
            unsafe_allow_html=True,
        )
    else:
        text = msg["content"]

        text_lower = text.lower()
        if "rating:" in text_lower:
            score_val = "5.0/10"
            verdict_val = ""
            roast_val = text

            for line in text.split("\n"):
                lower_line = line.lower()
                if lower_line.startswith("rating:"):
                    score_val = line[7:].strip()
                elif lower_line.startswith("verdict:"):
                    verdict_val = line[8:].strip()
                elif lower_line.startswith("roast:"):
                    roast_val = line[6:].strip()

            try:
                rating_num = float(score_val.split("/")[0])
                is_pos = rating_num >= 6.0
            except Exception:
                is_pos = True

            badge_class = "aura-score-pos" if is_pos else "aura-score-neg"
            verdict_span = (
                f'<span class="verdict-text" style="margin-left: 8px;">{verdict_val}</span>' if verdict_val else ""
            )

            bot_html = (
                f'<div class="msg-row-bot"><div class="msg-body-bot">'
                f'<div><span class="aura-score-badge {badge_class}">RATING: {score_val}</span>{verdict_span}</div>'
                f'<div class="roast-text">{roast_val}</div></div></div>'
            )
            st.markdown(bot_html, unsafe_allow_html=True)

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
                bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot" style="white-space: pre-wrap;">{text}</div></div>'
            else:
                diag_html = f'<div class="diagnosis-text">DIAGNOSIS: {diag_val}</div>' if diag_val else ""
                opts_html = "".join([f'<div class="option-item"><strong>{t}</strong> {b}</div>' for t, b in options])
                bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot">{diag_html}{opts_html}</div></div>'

            st.markdown(bot_html, unsafe_allow_html=True)

        else:
            bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot" style="white-space: pre-wrap;">{text}</div></div>'
            st.markdown(bot_html, unsafe_allow_html=True)

# ─── PENDING RESPONSE GENERATION ────────────────────────────────────────
if "pending_target" in st.session_state:
    curr_mode = st.session_state["pending_mode"]
    loading_verbs = {"JUDGE": "Judging...", "REFINE": "Rizzing...", "GENERATE": "Cooking..."}
    loading_text = loading_verbs.get(curr_mode, "Thinking...")

    loading_html = (
        f'<div class="loading-container"><div class="loading-text">'
        f"⏳ {loading_text}</div></div>"
    )
    st.markdown(loading_html, unsafe_allow_html=True)

st.markdown('<div id="chat-end-anchor" style="height: 40px; width: 100%;"></div>', unsafe_allow_html=True)

components.html(
    """
<script>
    setTimeout(() => {
        const doc = window.parent.document;
        const anchor = doc.getElementById('chat-end-anchor');
        if (anchor) {
            anchor.scrollIntoView({behavior: 'smooth', block: 'end'});
        }
    }, 100);
</script>
""",
    height=0,
)

if "pending_target" in st.session_state:
    target_to_process = st.session_state.pop("pending_target")
    curr_mode = st.session_state.pop("pending_mode")

    if (
        target_to_process.startswith("[JUDGE]")
        or target_to_process.startswith("[REFINE]")
        or target_to_process.startswith("[GENERATE]")
    ):
        full_prompt = target_to_process
    else:
        is_nsfw = "/nsfw" in target_to_process.lower()
        if is_nsfw:
            clean_target = re.sub(r'(?i)/nsfw\s*', '', target_to_process).strip()
            nsfw_tag = " /nsfw"
        else:
            clean_target = target_to_process
            nsfw_tag = ""

        if curr_mode == "JUDGE":
            full_prompt = f"[JUDGE] Line: '{clean_target}'"
        elif curr_mode == "REFINE":
            full_prompt = f"[REFINE]{nsfw_tag} Line: '{clean_target}'"
        else:
            full_prompt = f"[GENERATE]{nsfw_tag} {clean_target}"

    try:
        model_bundle = get_model(model_path, active_adapter)
        reply = generate_chat_response(model_bundle, full_prompt, curr_mode, max_tokens, temperature)
        st.session_state["messages"].append({"role": "assistant", "content": reply})
    except Exception as e:
        st.session_state["messages"].append({"role": "assistant", "content": f"Execution error: {str(e)}"})
    st.rerun()
