"""NewsMate AI - Streamlit MVP.   Run:  streamlit run app.py"""
import os
import tempfile

import streamlit as st

from newsmate import export, pipeline, transcribe

st.set_page_config(page_title="NewsMate AI", page_icon="📰", layout="wide")
S = st.session_state
for k, v in {"transcript": "", "translation": "", "summary": "", "pkg": None, "lang": ""}.items():
    S.setdefault(k, v)


@st.cache_resource(show_spinner="Loading speech model (first time downloads it)...")
def get_model(size):
    return transcribe.load_model(size)


st.title("📰 NewsMate AI")
st.caption("Your assistant drafts. You decide. Nothing is published without journalist approval.")

with st.sidebar:
    st.header("Settings")
    size = st.selectbox("Speech model", ["tiny", "base", "small", "medium"], index=2,
                        help="Bigger = more accurate but slower.")
    lang = st.selectbox("Spoken language", ["Auto-detect", "English", "Shona"])
    beat = st.text_input("Beat / topic", "general news")
    st.info("Ndebele speech recognition is not supported by Whisper. For Ndebele interviews, "
            "paste notes or a typed transcript instead.")
    if not os.getenv("ANTHROPIC_API_KEY"):
        st.warning("Set ANTHROPIC_API_KEY in your .env file.")

tabs = st.tabs(["1. Input", "2. Transcript", "3. Translate", "4. Generate", "5. Review & approve"])

# 1. INPUT
with tabs[0]:
    audio = st.file_uploader("Upload interview audio", type=["mp3", "wav", "m4a", "ogg", "mp4"])
    notes_in = st.text_area("...or paste interview notes / transcript", height=160)
    if st.button("Transcribe / load", type="primary"):
        if audio:
            with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(audio.name)[1]) as f:
                f.write(audio.read())
            code = {"Auto-detect": None, "English": "en", "Shona": "sn"}[lang]
            with st.spinner("Transcribing..."):
                segs, detected = transcribe.transcribe(get_model(size), f.name, code)
            os.unlink(f.name)
            S.transcript = transcribe.to_text(segs)
            S.lang = detected
            st.success(f"Done. Detected language: {detected}. Go to the Transcript tab.")
        elif notes_in.strip():
            S.transcript = notes_in.strip()
            st.success("Notes loaded. Go to the Transcript tab.")
        else:
            st.error("Upload audio or paste text first.")

# 2. TRANSCRIPT
with tabs[1]:
    st.write("Fix errors here. Lines ending in **??** were low-confidence, so check them against the audio.")
    S.transcript = st.text_area("Editable transcript", S.transcript, height=400)

# 3. TRANSLATE
with tabs[2]:
    target = st.radio("Translate to", list(pipeline.LANGUAGES), horizontal=True)
    if st.button("Translate"):
        with st.spinner("Translating..."):
            S.translation = pipeline.translate(S.transcript, target)
    if target in ("Shona", "Ndebele"):
        st.warning("Machine translation into Shona/Ndebele can be wrong. Have a fluent speaker review it.")
    S.translation = st.text_area("Translation", S.translation, height=300)
    if st.button("Summarise transcript"):
        with st.spinner("Summarising..."):
            S.summary = pipeline.summarise(S.transcript)
    if S.summary:
        st.markdown("**Summary**")
        st.markdown(S.summary)

# 4. GENERATE
with tabs[3]:
    notes = st.text_area("Extra context for the AI (optional: who, where, why it matters)")
    if st.button("Generate article, headlines & social posts", type="primary"):
        if not S.transcript.strip():
            st.error("No transcript yet.")
        else:
            with st.spinner("Drafting..."):
                try:
                    S.pkg = pipeline.build_package(S.transcript, notes, beat)
                    st.success("Draft ready. Go to Review & approve.")
                except Exception as e:
                    st.error(f"Generation failed: {e}")
    if S.pkg and S.pkg.get("open_questions"):
        st.markdown("**Verify before publishing:**")
        for q in S.pkg["open_questions"]:
            st.markdown(f"- {q}")

# 5. REVIEW
with tabs[4]:
    if not S.pkg:
        st.info("Generate a draft first.")
    else:
        p = S.pkg
        choice = st.radio("Pick a headline (or edit below)", p["headlines"])
        headline = st.text_input("Headline", choice)
        article = st.text_area("Article ([mm:ss] = where it came from in the audio)", p["article"], height=300)
        fb = st.text_area("Facebook", p["facebook"])
        xp = st.text_area("X post", p["x_post"])
        wa = st.text_area("WhatsApp", p["whatsapp"])
        st.caption(f"X length: {len(xp)}/280")
        name = st.text_input("Approving journalist's name")
        ok = st.checkbox("I have checked the facts, quotes and names, and approve this for publication.")
        if st.button("Approve & export", disabled=not (ok and name.strip())):
            md = export.to_markdown(
                {"headline": headline, "article": article, "facebook": fb, "x_post": xp, "whatsapp": wa}, name)
            st.download_button("Download publishing package (.md)", md, "newsmate_story.md", "text/markdown")
            st.code(md, language="markdown")
