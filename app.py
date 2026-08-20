import json
import os
import re
import sys
from pathlib import Path
import streamlit as st
import streamlit.components.v1 as components

sys.path.insert(0, str(Path(__file__).parent.resolve()))

st.set_page_config(
    page_title="Wingman",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ---------------------------------------------------------
# 1. UI STYLES
# ---------------------------------------------------------
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

    section[data-testid="stSidebar"] {
        display: none !important;
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
        /* Increased heavily to prevent the input bar from overlapping the final message */
        padding-bottom: 200px !important; 
    }

    /* Hide the communication text input entirely */
    div[data-testid="stTextInput"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
        width: 0 !important;
        position: absolute !important;
    }

    /* Header styling */
    .brand-group {
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 24px;
    }

    .brand-name {
        font-size: 22px;
        font-weight: 700;
        color: var(--primary);
        margin: 0;
    }

    .version-badge {
        background: #eef4f6;
        color: var(--primary);
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 4px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
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
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
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
        padding: 2px 6px;
        border-radius: 4px;
        margin-bottom: 6px;
    }
    .aura-score-pos { background: #eef4f6; color: var(--primary); }
    .aura-score-neg { background: #FDE8E7; color: #B52A25; }

    .verdict-text { font-weight: 700; color: var(--primary); margin-bottom: 6px; }
    .roast-text { color: var(--text-main); font-size: 15px; line-height: 1.6; }

    .diagnosis-text {
        color: var(--primary);
        font-weight: 700;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .option-item {
        margin-top: 8px;
        padding: 10px 14px;
        background-color: #f7f9fa;
        border: 1px solid var(--border-light);
        border-left: 3px solid var(--primary);
        border-radius: 0 10px 10px 0;
        font-size: 14px;
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
    .loading-text svg { animation: spin 2s linear infinite; }

    @keyframes pulse { 0% { opacity: 0.7; } 50% { opacity: 1; } 100% { opacity: 0.7; } }
    @keyframes spin { 100% { transform: rotate(360deg); } }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(6px); } to { opacity: 1; transform: translateY(0); } }

    /* Input container animation */
    div[data-testid="stBottom"] > div,
    div[data-testid="stChatInputContainer"] {
        background-color: transparent !important;
        background: transparent !important;
    }

    div[data-testid="stBottom"] {
        position: fixed !important;
        top: 50% !important;
        bottom: auto !important;
        transform: translate(-50%, -50%) !important;
        left: 50% !important;
        width: 90% !important;
        max-width: 760px !important;
        transition: top 0.45s cubic-bezier(0.16, 1, 0.3, 1), transform 0.45s cubic-bezier(0.16, 1, 0.3, 1) !important;
        z-index: 999 !important;
        background-color: transparent !important;
        background: transparent !important;
    }

    body.chat-active div[data-testid="stBottom"] {
        top: calc(100% - 24px) !important;
        transform: translate(-50%, -100%) !important;
    }

    /* FIXED Input Pill Styling */
    div[data-testid="stChatInput"] {
        background-color: #ffffff !important;
        border: 2px solid var(--primary) !important;
        border-radius: 34px !important;
        padding: 4px 6px 4px 20px !important;
        box-shadow: 0 6px 24px rgba(14, 95, 110, 0.08) !important;
    }
    
    div[data-testid="stChatInput"]:focus-within {
        box-shadow: 0 6px 24px rgba(14, 95, 110, 0.15) !important;
    }

    div[data-testid="stChatInput"] > div {
        background: transparent !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        align-items: center !important; 
    }

    div[data-testid="stChatInput"] textarea {
        background-color: transparent !important;
        color: var(--text-main) !important;
        font-size: 15px !important;
        caret-color: var(--primary) !important;
        padding-top: 12px !important;
        padding-bottom: 12px !important;
        min-height: 24px !important;
        line-height: 1.4 !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder { 
        color: var(--text-muted) !important;
        opacity: 1 !important;
    }

    /* Circular Send Button */
    div[data-testid="stChatInput"] button {
        background-color: var(--primary) !important;
        border: none !important;
        border-radius: 50% !important;
        width: 38px !important;
        height: 38px !important;
        min-width: 38px !important;
        min-height: 38px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: background-color 0.2s, transform 0.1s !important;
        align-self: center !important;
        margin: 0 !important;
        padding: 0 !important;
        position: relative !important;
        z-index: 11 !important;
    }

    div[data-testid="stChatInput"] button:hover {
        background-color: var(--primary-hover) !important;
    }

    div[data-testid="stChatInput"] button:active {
        transform: scale(0.94) !important;
    }

    div[data-testid="stChatInput"] button svg {
        fill: none !important;
        stroke: #ffffff !important;
        stroke-width: 2.5 !important;
        width: 16px !important;
        height: 16px !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ---------------------------------------------------------
# 2. BACKEND LOGIC 
# ---------------------------------------------------------
@st.cache_resource
def get_mlx_model(model_path: str, adapter_path: str | None):
    import mlx.core as mx
    import mlx_lm
    mx.set_default_device(mx.gpu)

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

    return model, tokenizer

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

def generate_chat_response(model, tokenizer, prompt_str: str, max_tokens: int, temp: float) -> str:
    import mlx.core as mx
    import mlx_lm
    from mlx_lm.sample_utils import make_sampler
    mx.set_default_device(mx.gpu)
    messages = [{"role": "user", "content": prompt_str.strip()}]
    formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    sampler = make_sampler(temp=temp)

    raw_response = mlx_lm.generate(
        model,
        tokenizer,
        prompt=formatted_prompt,
        max_tokens=max_tokens,
        sampler=sampler,
        verbose=False
    )
    return clean_response(raw_response)

model_path = "models/Qwen2.5-1.5B"
active_adapter = (
    "outputs/qwen2.5-1.5b-wingman-lora/adapters"
    if os.path.exists("outputs/qwen2.5-1.5b-wingman-lora/adapters")
    else "outputs/smoke-test/adapters"
)
temperature = 0.7
max_tokens = 256


# ---------------------------------------------------------
# 3. STATE MANAGEMENT & LAYOUT
# ---------------------------------------------------------
if "messages" not in st.session_state:
    st.session_state["messages"] = []

nav_l, nav_r = st.columns([4, 1])
with nav_l:
    st.markdown('<div class="brand-group"><h1 class="brand-name">Wingman</h1></div>', unsafe_allow_html=True)
with nav_r:
    if st.button("New Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

# Minimal JS strictly to toggle the centered/bottom position
components.html(f"""
<script>
(function() {{
    const hasMessages = {str(bool(st.session_state['messages'])).lower()};
    if (hasMessages) {{
        window.parent.document.body.classList.add('chat-active');
    }} else {{
        window.parent.document.body.classList.remove('chat-active');
    }}
}})();
</script>
""", height=0)

for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        # Flat string to prevent Markdown parsing it as code
        st.markdown(f'<div class="msg-row-user"><div class="msg-bubble-user">{msg["content"]}</div></div>', unsafe_allow_html=True)
    else:
        text = msg["content"]

        if "Aura:" in text or "Verdict:" in text:
            aura_val = "0"
            verdict_val = ""
            roast_val = text

            for line in text.split("\n"):
                if line.startswith("Aura:"):
                    aura_val = line.replace("Aura:", "").strip()
                elif line.startswith("Verdict:"):
                    verdict_val = line.replace("Verdict:", "").strip()
                elif line.startswith("Roast:"):
                    roast_val = line.replace("Roast:", "").strip()

            is_pos = "+" in aura_val or ("-" not in aura_val and aura_val != "0")
            badge_class = "aura-score-pos" if is_pos else "aura-score-neg"
            verdict_span = f'<span class="verdict-text" style="margin-left: 8px;">{verdict_val}</span>' if verdict_val else ''
            
            # Flat string
            bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot"><div><span class="aura-score-badge {badge_class}">AURA: {aura_val}</span>{verdict_span}</div><div class="roast-text">{roast_val}</div></div></div>'
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
                diag_html = f'<div class="diagnosis-text">DIAGNOSIS: {diag_val}</div>' if diag_val else ''
                opts_html = "".join([f'<div class="option-item"><strong>{t}</strong> {b}</div>' for t, b in options])
                # Flat string
                bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot">{diag_html}{opts_html}</div></div>'
            
            st.markdown(bot_html, unsafe_allow_html=True)

        else:
            bot_html = f'<div class="msg-row-bot"><div class="msg-body-bot" style="white-space: pre-wrap;">{text}</div></div>'
            st.markdown(bot_html, unsafe_allow_html=True)

# ---------------------------------------------------------
# Spacer - Triggers Streamlit auto-scroll safely past the fixed input bar
# ---------------------------------------------------------
st.markdown('<div style="height: 100px; width: 100%;"></div>', unsafe_allow_html=True)

# ---------------------------------------------------------
# 4. INPUT & GENERATION
# ---------------------------------------------------------
user_input = st.chat_input("Use /judge, /refine, or /gen followed by your text...")

if user_input:
    input_text = user_input.strip()
    lower_input = input_text.lower()
    
    # Immediately display user message
    st.session_state["messages"].append({"role": "user", "content": input_text})
    st.markdown(f'<div class="msg-row-user"><div class="msg-bubble-user">{input_text}</div></div>', unsafe_allow_html=True)

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
        if target_to_process.startswith("[JUDGE]") or target_to_process.startswith("[REFINE]") or target_to_process.startswith("[GENERATE]"):
            full_prompt = target_to_process
        else:
            if curr_mode == "JUDGE":
                full_prompt = f"[JUDGE] Line: '{target_to_process}'"
            elif curr_mode == "REFINE":
                full_prompt = f"[REFINE] Line: '{target_to_process}'"
            else:
                if not target_to_process.lower().startswith("scenario:"):
                    full_prompt = f"[GENERATE] Scenario: {target_to_process}"
                else:
                    full_prompt = f"[GENERATE] {target_to_process}"

        loading_placeholder = st.empty()
        loading_verbs = {"JUDGE": "Judging...", "REFINE": "Rizzing...", "GENERATE": "Cooking..."}
        loading_text = loading_verbs.get(curr_mode, "Thinking...")

        # Single string to prevent code block parsing
        loading_html = f'''<div class="loading-container"><div class="loading-text"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="2" x2="12" y2="6"></line><line x1="12" y1="18" x2="12" y2="22"></line><line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line><line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line><line x1="2" y1="12" x2="6" y2="12"></line><line x1="18" y1="12" x2="22" y2="12"></line><line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line><line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line></svg> {loading_text}</div></div>'''
        loading_placeholder.markdown(loading_html, unsafe_allow_html=True)

        try:
            model, tokenizer = get_mlx_model(model_path, active_adapter)
            reply = generate_chat_response(model, tokenizer, full_prompt, max_tokens, temperature)
            st.session_state["messages"].append({"role": "assistant", "content": reply})
        except Exception as e:
            st.session_state["messages"].append({"role": "assistant", "content": f"Execution error: {str(e)}"})

        loading_placeholder.empty()
        st.rerun()

    else:
        guide_message = (
            "**Oops! Please use a command to tell Wingman what to do.**\n\n"
            "• `/judge [text]` — Rate a pickup line or message\n"
            "• `/refine [text]` — Polish your draft\n"
            "• `/gen [scenario]` — Generate openers or ideas"
        )
        st.session_state["messages"].append({"role": "assistant", "content": guide_message})
        st.rerun()