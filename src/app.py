import os
import streamlit as st
import joblib
import numpy as np

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "deepsea_model_v1.pkl")

@st.cache_resource
def load_model():
    model = joblib.load(MODEL_PATH)
    return model

def interpret_score(score: float):
    """
    Interpret probability that the text is Emotional Affair / Hot (class 1).
    Returns a (verdict, description).
    """
    if score < 0.3:
        verdict = "✅ Likely Platonic / Cold Communication"
        desc = (
            "Model sees this as primarily side-by-side or task-focused. "
            "Emotional dependence cues are low."
        )
    elif score < 0.7:
        verdict = "🟡 Mixed / Ambiguous Signals"
        desc = (
            "Model detects both intellectual and emotional-dependence signals. "
            "Boundaries may be blurred in places, but pattern is not strongly one-sided."
        )
    else:
        verdict = "⚠️ High Emotional-Affair Risk"
        desc = (
            "Model detects strong ‘face-to-face’ emotional gratification signals: "
            "high emotional dependency, privacy/invasion of boundaries, or romantic-style texting patterns."
        )
    return verdict, desc

def main():
    st.set_page_config(page_title="DeepSea Friendship Auditor", page_icon="🌊")
    st.title("🌊 DeepSea Friendship Auditor")
    st.write(
        "Classifies chat snippets along your theory of **Platonic / Cold** vs **Emotional Affair / Hot** communication.\n\n"
        "Paste a conversation (e.g., a short chat log between two people). "
        "The model will estimate how much it resembles an *emotional affair style* interaction."
    )

    model = load_model()

    st.subheader("Input Conversation")
    default_example = (
        "A: Good morning, did you sleep well? ☺️\n"
        "B: Morning 💕 I was waiting for your message.\n"
        "A: I didn't tell my partner we talk this much, please don't say anything.\n"
        "B: It's okay, this is our little world."
    )

    text = st.text_area(
        "Paste chat here:",
        value=default_example,
        height=200,
        help="Include multiple lines with speaker labels if you like. "
             "The model treats the whole block as one document."
    )

    if st.button("Analyze"):
        if not text.strip():
            st.warning("Please paste some text first.")
            return

        # Model expects an iterable of texts
        proba = model.predict_proba([text])[0]
        # Assuming class order is [0, 1]; get probability of class 1
        # (you can check `model.classes_` if you want to be absolutely sure)
        p_hot = float(proba[1])
        verdict, desc = interpret_score(p_hot)

        st.subheader("Result")

        st.markdown(f"**Emotional-Affair Risk Score (Class 1 probability):** `{p_hot:.2f}`")

        st.progress(p_hot)  # visual bar from 0 to 1

        st.markdown(f"### {verdict}")
        st.write(desc)

        st.markdown("#### Model Perspective")
        st.write(
            "- This is **not** a moral judgment, just a statistical pattern match.\n"
            "- Use it as a **conversation starter** or self-reflection tool, not as final proof of anything.\n"
            "- Future versions could incorporate conversation history, time gaps, and per-speaker patterns."
        )

    st.markdown("---")
    st.caption(
        "Prototype NLP tool. For educational and reflective purposes only; "
        "not psychological, legal, or relationship advice."
    )

if __name__ == "__main__":
    main()
