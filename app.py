import json
import os
import re
import sys
from pathlib import Path
import streamlit as st

sys.path.insert(0, str(Path(__file__).parent.resolve()))

st.set_page_config(
    page_title="Wingman",
    layout="centered",
    initial_sidebar_state="collapsed"
)

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --teal-dark: #006078;
        --teal-sky: #82BAC4;
        --bg-main: #FAF7F5;
        --peach-soft: #FFD4D1;
        --coral-accent: #E37C78;
        --slate-dark: #1E293B;
        --slate-muted: #64748B;
        --card-bg: #FFFFFF;
        --border-color: #E2E8F0;
    }

    section[data-testid="stSidebar"] {
        display: none !important;
    }

    .stApp {
        background-color: var(--bg-main) !important;
        color: var(--slate-dark) !important;
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    }

    header[data-testid="stHeader"] {
        background-color: transparent !important;
    }

    .main .block-container {
        max-width: 720px !important;
        padding-top: 20px !important;
        padding-bottom: 120px !important;
    }

    .brand-group {
        display: flex;
        align-items: center;
        gap: 8px;
    }

    .brand-name {
        font-size: 22px;
        font-weight: 800;
        color: var(--teal-dark);
        letter-spacing: -0.5px;
        margin: 0;
    }

    .version-badge {
        background-color: #E2F0F3;
        color: var(--teal-dark);
        font-size: 11px;
        font-weight: 700;
        padding: 2px 8px;
        border-radius: 12px;
        border: 1px solid var(--teal-sky);
        letter-spacing: 0.5px;
    }

    .hero-container {
        text-align: center;
        padding: 32px 0 24px 0;
    }

    .hero-title {
        font-size: 32px;
        font-weight: 800;
        color: var(--teal-dark);
        letter-spacing: -0.8px;
        margin-bottom: 8px;
    }

    .hero-subtitle {
        font-size: 15px;
        color: var(--slate-muted);
        max-width: 540px;
        margin: 0 auto 32px auto;
        line-height: 1.5;
    }

    .msg-row-user {
        display: flex;
        justify-content: flex-end;
        margin-bottom: 20px;
    }

    .msg-bubble-user {
        background: linear-gradient(135deg, var(--teal-dark) 0%, #004D60 100%);
        color: #FFFFFF;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 80%;
        font-size: 15px;
        line-height: 1.5;
        box-shadow: 0 4px 12px rgba(0, 96, 120, 0.15);
        word-wrap: break-word;
    }

    .msg-row-bot {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 24px;
    }

    .msg-body-bot {
        color: var(--slate-dark);
        max-width: 100%;
        font-size: 15px;
        line-height: 1.6;
        padding: 4px 0;
    }

    .aura-score-badge {
        display: inline-block;
        font-weight: 700;
        font-size: 13px;
        padding: 3px 12px;
        border-radius: 12px;
        margin-bottom: 8px;
    }

    .aura-score-pos {
        background-color: #E2F4EE;
        color: #0E6B50;
        border: 1px solid #A3E1CF;
    }

    .aura-score-neg {
        background-color: #FDE8E7;
        color: #B52A25;
        border: 1px solid var(--coral-accent);
    }

    .verdict-text {
        font-weight: 700;
        color: var(--teal-dark);
        margin-bottom: 6px;
    }

    .roast-text {
        color: var(--slate-dark);
        font-size: 15px;
        line-height: 1.6;
    }

    .diagnosis-text {
        color: var(--coral-accent);
        font-weight: 700;
        font-size: 13px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }

    .option-item {
        margin-top: 8px;
        padding: 10px 14px;
        background-color: rgba(255, 255, 255, 0.7);
        border: 1px solid var(--border-color);
        border-left: 3px solid var(--teal-dark);
        border-radius: 0 10px 10px 0;
        font-size: 14px;
        line-height: 1.5;
    }

    .option-item strong {
        color: var(--teal-dark);
        display: block;
        font-size: 12px;
        text-transform: uppercase;
        margin-bottom: 3px;
    }

    .loading-container {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 24px;
    }

    .loading-text {
        font-size: 14px;
        font-weight: 600;
        color: var(--teal-sky);
        display: flex;
        align-items: center;
        gap: 8px;
        animation: pulse 1.5s infinite;
        padding: 8px 14px;
        background-color: var(--card-bg);
        border: 1px solid var(--border-color);
        border-radius: 18px 18px 18px 4px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.02);
    }

    .loading-text svg {
        animation: spin 2s linear infinite;
    }

    @keyframes pulse {
        0% { opacity: 0.7; }
        50% { opacity: 1; }
        100% { opacity: 0.7; }
    }

    @keyframes spin {
        100% { transform: rotate(360deg); }
    }

    footer {
        display: none !important;
    }

    div[data-testid="stBottom"],
    div[data-testid="stBottom"] > div,
    div[data-testid="stChatInputContainer"] {
        background-color: var(--bg-main) !important;
        background: var(--bg-main) !important;
    }

    div[data-testid="stBottom"] > div {
        max-width: 720px !important;
        margin: 0 auto !important;
        padding-bottom: 14px !important;
    }

    div[data-testid="stChatInput"] {
        background-color: #FFFFFF !important;
        background: #FFFFFF !important;
        border: 1.5px solid #CBD5E1 !important;
        border-radius: 28px !important;
        box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06) !important;
        padding: 4px 10px !important;
    }

    div[data-testid="stChatInput"] * {
        background-color: transparent !important;
    }

    div[data-testid="stChatInput"] textarea {
        color: var(--slate-dark) !important;
        font-size: 15px !important;
        caret-color: var(--teal-dark) !important;
    }

    div[data-testid="stChatInput"] textarea::placeholder {
        color: var(--slate-muted) !important;
        opacity: 0.7 !important;
    }

    div[data-testid="stChatInput"]:focus-within {
        border-color: var(--teal-dark) !important;
        box-shadow: 0 8px 30px rgba(0, 96, 120, 0.12) !important;
    }

    div[data-testid="stChatInput"] button {
        background-color: var(--teal-dark) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: 50% !important;
        width: 34px !important;
        height: 34px !important;
        min-width: 34px !important;
        min-height: 34px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        transition: all 0.15s ease !important;
        box-shadow: 0 2px 8px rgba(0, 96, 120, 0.2) !important;
    }

    div[data-testid="stChatInput"] button:hover {
        transform: scale(1.08) !important;
        background-color: #004D60 !important;
    }

    div[data-testid="stChatInput"] button svg {
        fill: #FFFFFF !important;
        stroke: #FFFFFF !important;
        width: 18px !important;
        height: 18px !important;
    }

    .stButton>button {
        background-color: var(--card-bg) !important;
        color: var(--teal-dark) !important;
        border: 1.5px solid var(--teal-sky) !important;
        border-radius: 16px !important;
        font-weight: 600 !important;
        padding: 5px 18px !important;
        font-size: 13px !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
        transition: all 0.15s ease !important;
    }

    .stButton>button:hover {
        background-color: var(--peach-soft) !important;
        border-color: var(--coral-accent) !important;
        color: var(--teal-dark) !important;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


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


if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "mode" in st.query_params:
    st.session_state["mode"] = st.query_params["mode"].upper()
elif "mode" not in st.session_state:
    st.session_state["mode"] = "JUDGE"

nav_l, nav_r = st.columns([4, 1])
with nav_l:
    st.markdown(
        """
        <div class="brand-group">
            <h1 class="brand-name">Wingman</h1>
            <span class="version-badge">v2.0</span>
        </div>
        """,
        unsafe_allow_html=True
    )
with nav_r:
    if st.button("New Chat", use_container_width=True):
        st.session_state["messages"] = []
        st.rerun()

preset_trigger = None

if not st.session_state["messages"]:


    card_c1, card_c2, card_c3 = st.columns(3)

    with card_c1:
        if st.button(
            "Judge & Roast\n\nPaste a risky opener to get a brutal aura score and critique.",
            use_container_width=True,
            key="card_judge"
        ):
            st.session_state["mode"] = "JUDGE"
            st.query_params["mode"] = "judge"
            preset_trigger = "Are you a magician? Because whenever I look at you, everyone else disappears."

    with card_c2:
        if st.button(
            "Refine & Upgrade\n\nTurn dry, one-word replies into playful, high-energy banter.",
            use_container_width=True,
            key="card_refine"
        ):
            st.session_state["mode"] = "REFINE"
            st.query_params["mode"] = "refine"
            preset_trigger = "hru"

    with card_c3:
        if st.button(
            "Generate Hooks\n\nUse a match bio or hobby context to craft personalized openers.",
            use_container_width=True,
            key="card_generate"
        ):
            st.session_state["mode"] = "GENERATE"
            st.query_params["mode"] = "generate"
            preset_trigger = "Bio says 'Probably listening to deftones, obsessed with film cameras, and drinking black coffee at 2 AM.'"

for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.markdown(
            f"""
            <div class="msg-row-user">
                <div class="msg-bubble-user">{msg["content"]}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
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

            bot_html = f"""
            <div class="msg-row-bot">
                <div class="msg-body-bot">
                    <div>
                        <span class="aura-score-badge {badge_class}">AURA: {aura_val}</span>
                        {f'<span class="verdict-text" style="margin-left: 8px;">{verdict_val}</span>' if verdict_val else ''}
                    </div>
                    <div class="roast-text">{roast_val}</div>
                </div>
            </div>
            """
            st.markdown(bot_html, unsafe_allow_html=True)

        elif "Diagnosis:" in text or "Option 1" in text:
            diag_val = ""
            options = []
            for line in text.split("\n"):
                if line.startswith("Diagnosis:"):
                    diag_val = line.replace("Diagnosis:", "").strip()
                elif line.startswith("Option"):
                    parts = line.split(":", 1)
                    t = parts[0].strip()
                    b = parts[1].strip() if len(parts) > 1 else ""
                    options.append((t, b))

            opts_html = "".join([
                f'<div class="option-item"><strong>{t}</strong>{b}</div>'
                for t, b in options
            ])

            diag_html = f'<div class="diagnosis-text">Diagnosis: {diag_val}</div>' if diag_val else ''

            bot_html = f"""
            <div class="msg-row-bot">
                <div class="msg-body-bot">
                    {diag_html}
                    {opts_html}
                </div>
            </div>
            """
            st.markdown(bot_html, unsafe_allow_html=True)

        else:
            st.markdown(
                f"""
                <div class="msg-row-bot">
                    <div class="msg-body-bot" style="white-space: pre-wrap;">{text}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


placeholder_map = {
    "JUDGE": "Message Wingman to judge a pick-up line...",
    "REFINE": "Message Wingman to refine a dry text...",
    "GENERATE": "Message Wingman to generate openers from a bio..."
}

current_mode = st.session_state["mode"]
mode_labels = ["Judge", "Refine", "Generate"]
mode_keys = ["JUDGE", "REFINE", "GENERATE"]
current_idx = mode_keys.index(current_mode)

import streamlit.components.v1 as components

components.html(f"""
<script>
(function() {{
    function inject() {{
        const chatInput = parent.document.querySelector('div[data-testid="stChatInput"]');
        if (!chatInput) {{ setTimeout(inject, 300); return; }}
        if (chatInput.querySelector('.wm-mode-select')) return;

        chatInput.style.position = 'relative';

        const wrap = document.createElement('div');
        wrap.style.cssText = 'position:absolute;right:52px;top:50%;transform:translateY(-50%);z-index:10;';

        const sel = document.createElement('select');
        sel.className = 'wm-mode-select';
        sel.style.cssText = `
            appearance:none;-webkit-appearance:none;
            background:transparent;
            border:1px solid #CBD5E1;border-radius:14px;
            padding:5px 26px 5px 12px;
            font-size:13px;font-weight:600;color:#006078;
            cursor:pointer;outline:none;
            font-family:'Plus Jakarta Sans',sans-serif;
            background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='10' height='10' viewBox='0 0 24 24' fill='none' stroke='%23006078' stroke-width='3' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpath d='M6 9l6 6 6-6'/%3E%3C/svg%3E");
            background-repeat:no-repeat;background-position:right 8px center;background-size:10px;
        `;

        ['Judge','Refine','Generate'].forEach((label, i) => {{
            const opt = document.createElement('option');
            opt.value = ['JUDGE','REFINE','GENERATE'][i];
            opt.textContent = label;
            if (i === {current_idx}) opt.selected = true;
            sel.appendChild(opt);
        }});

        sel.onmouseenter = () => {{ sel.style.borderColor='#006078'; sel.style.background='#E2F0F3'; }};
        sel.onmouseleave = () => {{ sel.style.borderColor='#CBD5E1'; sel.style.background='transparent'; }};

        sel.onchange = (e) => {{
            const newMode = e.target.value.toLowerCase();
            const url = new URL(window.parent.location);
            url.searchParams.set("mode", newMode);
            window.parent.history.pushState({{}}, "", url);
            
            const ta = chatInput.querySelector('textarea');
            if (ta) {{
                if (newMode === 'judge') ta.placeholder = 'Message Wingman to judge a pick-up line...';
                else if (newMode === 'refine') ta.placeholder = 'Message Wingman to refine a dry text...';
                else ta.placeholder = 'Message Wingman to generate openers from a bio...';
            }}
        }};

        wrap.appendChild(sel);
        chatInput.appendChild(wrap);
    }}
    inject();
}})();
</script>
""", height=0)

user_input = st.chat_input(placeholder_map.get(current_mode, "Message Wingman..."))

target_to_process = None

if user_input:
    lowered = user_input.strip().lower()
    if lowered == "/mode judge":
        st.session_state["mode"] = "JUDGE"
        st.rerun()
    elif lowered == "/mode refine":
        st.session_state["mode"] = "REFINE"
        st.rerun()
    elif lowered == "/mode generate":
        st.session_state["mode"] = "GENERATE"
        st.rerun()
    else:
        target_to_process = user_input

if preset_trigger:
    target_to_process = preset_trigger

if target_to_process:
    curr_mode = st.session_state["mode"]

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

    st.session_state["messages"].append({
        "role": "user",
        "content": target_to_process
    })

    st.markdown(
        f"""
        <div class="msg-row-user">
            <div class="msg-bubble-user">{target_to_process}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    loading_placeholder = st.empty()
    loading_verbs = {
        "JUDGE": "Judging...",
        "REFINE": "Rizzing...",
        "GENERATE": "Cooking..."
    }
    loading_text = loading_verbs.get(curr_mode, "Thinking...")

    loading_placeholder.markdown(
        f"""
        <div class="loading-container">
            <div class="loading-text">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="2" x2="12" y2="6"></line>
                    <line x1="12" y1="18" x2="12" y2="22"></line>
                    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                    <line x1="2" y1="12" x2="6" y2="12"></line>
                    <line x1="18" y1="12" x2="22" y2="12"></line>
                    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                </svg>
                {loading_text}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    try:
        model, tokenizer = get_mlx_model(model_path, active_adapter)
        reply = generate_chat_response(model, tokenizer, full_prompt, max_tokens, temperature)
        st.session_state["messages"].append({
            "role": "assistant",
            "content": reply
        })
    except Exception as e:
        st.session_state["messages"].append({
            "role": "assistant",
            "content": f"Execution error: {str(e)}"
        })

    loading_placeholder.empty()
    st.rerun()

