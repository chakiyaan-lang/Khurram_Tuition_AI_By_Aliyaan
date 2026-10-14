import os
import requests
import streamlit as st

st.set_page_config(page_title="Khurram's AI | School Tutor", page_icon="🎓", layout="wide")

# A simple, responsive interface designed for school students.
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
html, body, [class*="css"] { font-family: Inter, sans-serif; }
.stApp { background: radial-gradient(ellipse at top left, #172554 0%, #0b1224 45%, #080d19 100%); color: #eef2ff; }
section[data-testid="stSidebar"] { background: #101a30; border-right: 1px solid #263653; }
.hero { padding: 1.8rem 2rem; border: 1px solid #304469; border-radius: 24px; background: linear-gradient(120deg, rgba(30,58,138,.68), rgba(76,29,149,.45)); margin-bottom: 1.2rem; }
.eyebrow { color: #93c5fd; font-size: .78rem; font-weight: 800; letter-spacing: .16em; text-transform: uppercase; }
.hero h1 { color: #fff; font-size: clamp(2rem, 4vw, 3.3rem); line-height: 1.1; margin: .55rem 0; }
.hero p { color: #dbeafe; max-width: 760px; font-size: 1.05rem; }
.pill { display:inline-block; padding:.35rem .7rem; margin:.2rem .25rem .2rem 0; border-radius:999px; background:#172554; border:1px solid #3b5992; color:#bfdbfe; font-size:.8rem; }
div[data-testid="stChatMessage"] { background: rgba(17, 28, 51, .78); border: 1px solid #253653; border-radius: 16px; padding: .8rem; }
.stButton > button { border-radius: 12px; border: 1px solid #4666a2; }
small, .muted { color:#a9b8d4; }
</style>
<div class="hero">
  <div class="eyebrow">Your personal school learning companion</div>
  <h1>Khurram’s AI 🎓</h1>
  <p>A friendly study assistant for Pakistani students in Classes 1–10, with extra support for Classes 9 and 10. Learn concepts, practise questions, and prepare for exams step by step.</p>
  <span class="pill">Classes 1–10</span><span class="pill">Pakistan-focused</span><span class="pill">Step-by-step explanations</span>
</div>
""", unsafe_allow_html=True)

SUBJECTS = ["Mathematics", "Physics", "Chemistry", "Biology", "Computer Science", "English", "Urdu", "Pakistan Studies", "Islamiat", "General Science", "Other"]
BOARDS = ["Punjab / PCTB", "Sindh / STBB", "Federal / FBISE", "Khyber Pakhtunkhwa", "Balochistan", "Other / Not sure"]
LANGUAGES = ["English", "Urdu", "Roman Urdu", "English + Urdu"]
DETAILS = ["Short and clear", "Detailed explanation", "Exam-style answer"]

with st.sidebar:
    st.markdown("## ⚙️ Study settings")
    grade = st.selectbox("Your class", [f"Class {i}" for i in range(1, 11)], index=8)
    subject = st.selectbox("Subject", SUBJECTS, index=0)
    board = st.selectbox("Board / curriculum", BOARDS, index=0)
    language = st.selectbox("Answer language", LANGUAGES, index=0)
    detail = st.selectbox("Explanation style", DETAILS, index=1)
    st.divider()
    st.markdown("### Quick tips")
    st.caption("• Share the exact question for a better answer.\n\n• For textbook questions, paste the text or upload a clear photo if your interface supports it.\n\n• Always check important answers against your teacher or textbook.")
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

SYSTEM_PROMPT = """You are Khurram's AI, a patient, accurate school tutor for students in Pakistan. Help students learn rather than merely copy answers. Adapt to the selected class, subject, board and language. Use age-appropriate explanations and Pakistani school terminology. For mathematics, show the formula, substitution, calculations and final answer. For science, explain concepts simply and distinguish facts from uncertainty. For exam-style questions, give a clear answer with useful headings. Never claim to know the exact latest textbook or syllabus unless the user provides it. If a question depends on a particular textbook edition, ask the student to paste the question or relevant passage. If unsure, say so. Do not help students cheat during a live exam; offer learning support instead."""

if "messages" not in st.session_state:
    st.session_state.messages = []

# Try an optional Hugging Face Inference API configuration first; otherwise use a
# public tokenless endpoint as a convenience fallback. Public endpoints may change,
# rate-limit requests, or be unavailable; this app cannot guarantee free unlimited AI.
def get_ai_reply(history, prompt, settings):
    context = (
        f"Student settings: {settings['grade']}; subject: {settings['subject']}; "
        f"board: {settings['board']}; answer language: {settings['language']}; "
        f"style: {settings['detail']}.\n\n"
    )
    transcript = []
    for item in history[-8:]:
        role = "Student" if item["role"] == "user" else "Tutor"
        transcript.append(f"{role}: {item['content']}")
    full_prompt = SYSTEM_PROMPT + "\n\n" + context + "\n".join(transcript) + f"\nStudent: {prompt}\nTutor:"

    token = os.getenv("HF_TOKEN", "").strip()
    if token:
        try:
            from huggingface_hub import InferenceClient
            model = os.getenv("HF_MODEL", "Qwen/Qwen2.5-7B-Instruct")
            client = InferenceClient(model=model, token=token, timeout=60)
            chat_messages = [{"role": "system", "content": SYSTEM_PROMPT + "\n" + context}]
            for item in history[-8:]:
                chat_messages.append({"role": item["role"], "content": item["content"]})
            chat_messages.append({"role": "user", "content": prompt})
            result = client.chat_completion(messages=chat_messages, max_tokens=900, temperature=0.4)
            return result.choices[0].message.content
        except Exception:
            # If an optional HF configuration fails, try the no-token fallback.
            pass

    try:
        response = requests.get(
            "https://text.pollinations.ai/" + requests.utils.quote(full_prompt, safe=""),
            timeout=90,
            headers={"User-Agent": "KhurramsAI/1.0"},
        )
        response.raise_for_status()
        answer = response.text.strip()
        if not answer:
            raise ValueError("The AI service returned an empty answer.")
        return answer
    except Exception as exc:
        raise RuntimeError(
            "The free public AI service did not respond. It may be temporarily unavailable or rate-limited. "
            "Please try again later. No API token is required for the default setup. "
            f"(Technical detail: {type(exc).__name__})"
        ) from exc

settings = {"grade": grade, "subject": subject, "board": board, "language": language, "detail": detail}

if not st.session_state.messages:
    st.markdown("### What would you like to learn today?")
    cols = st.columns(3)
    examples = [
        ("➗ Maths help", "Explain how to solve a linear equation with one example."),
        ("🧪 Science concept", "Explain atoms and molecules in simple words."),
        ("📝 Exam practice", "Give me 5 practice questions for my selected class and subject, with answers hidden until I ask."),
    ]
    for col, (label, prompt) in zip(cols, examples):
        with col:
            if st.button(label, use_container_width=True):
                st.session_state.pending_prompt = prompt
                st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Ask a school question…")
if not prompt and st.session_state.get("pending_prompt"):
    prompt = st.session_state.pop("pending_prompt")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    with st.chat_message("assistant"):
        with st.spinner("Khurram’s AI is thinking…"):
            try:
                answer = get_ai_reply(st.session_state.messages[:-1], prompt, settings)
                st.markdown(answer)
            except RuntimeError as err:
                answer = str(err)
                st.warning(answer)
                st.caption("If this keeps happening, the public endpoint may be unavailable. An optional Hugging Face token can be added later in Streamlit Secrets, but it is not required to deploy this project.")
    st.session_state.messages.append({"role": "assistant", "content": answer})

st.divider()
st.caption("Khurram’s AI is an independent study helper, not an official school or examination-board service. AI answers can be incorrect. The default public AI endpoint is third-party and may have limits, downtime, or changing terms. Do not enter passwords, private information, or other sensitive data.")
