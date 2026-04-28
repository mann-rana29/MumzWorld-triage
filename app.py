import json
from pathlib import Path

import streamlit as st

from triage import triage_email
from schema import TriageOutput

SAMPLE_EMAILS_PATH = Path(__file__).parent / "data" / "sample_emails.json"

URGENCY_COLORS = {
    "high": "#e74c3c",
    "medium": "#f39c12",
    "low": "#2ecc71",
}

URGENCY_LABELS = {
    "high": "HIGH",
    "medium": "MEDIUM",
    "low": "LOW",
}


def load_sample_emails():
    if not SAMPLE_EMAILS_PATH.exists():
        return []
    return json.loads(SAMPLE_EMAILS_PATH.read_text(encoding="utf-8"))


def render_urgency_badge(urgency: str):
    color = URGENCY_COLORS.get(urgency, "#95a5a6")
    label = URGENCY_LABELS.get(urgency, urgency.upper())
    st.markdown(
        f'<span style="background-color:{color};color:white;padding:4px 12px;'
        f'border-radius:12px;font-weight:600;font-size:14px;">'
        f'{label}</span>',
        unsafe_allow_html=True,
    )


def render_intent_tag(intent: str):
    st.markdown(
        f'<span style="background-color:#3498db;color:white;padding:4px 12px;'
        f'border-radius:12px;font-weight:600;font-size:14px;">'
        f'{intent.replace("_", " ").title()}</span>',
        unsafe_allow_html=True,
    )


def render_results(result: TriageOutput):
    st.markdown("---")
    st.subheader("Triage Results")

    col1, col2, col3 = st.columns([1, 1, 2])
    with col1:
        st.markdown("**Urgency**")
        render_urgency_badge(result.urgency)
    with col2:
        st.markdown("**Intent**")
        render_intent_tag(result.intent)
    with col3:
        st.markdown("**Confidence**")
        st.progress(result.confidence)
        st.caption(f"{result.confidence:.0%}")

    lang_labels = {"en": "English", "ar": "Arabic", "mixed": "Mixed", "unknown": "Unknown"}
    st.markdown(f"**Language Detected:** {lang_labels.get(result.language_detected, result.language_detected)}")

    if result.escalate:
        st.warning("ESCALATION REQUIRED — This email needs human review. Auto-reply suppressed.")

    if not result.escalate:
        st.markdown("### Suggested Replies")
        en_col, ar_col = st.columns(2)
        with en_col:
            st.markdown("**English Reply**")
            if result.suggested_reply_en:
                st.info(result.suggested_reply_en)
            else:
                st.caption("No reply generated")
        with ar_col:
            st.markdown("**Arabic Reply**")
            if result.suggested_reply_ar:
                st.markdown(
                    f'<div dir="rtl" style="background-color:#111111;padding:12px;'
                    f'border-radius:8px;font-size:16px;line-height:1.8;">'
                    f'{result.suggested_reply_ar}</div>',
                    unsafe_allow_html=True,
                )
            else:
                st.caption("No reply generated")

    with st.expander("Reasoning"):
        st.write(result.reasoning)
        st.caption(f"Model: {result.model_version}")


def main():
    st.set_page_config(
        page_title="Mumzworld CS Triage",
        layout="wide",
    )

    st.title("Mumzworld CS Email Triage")
    st.caption("AI-powered customer service email classification and response generation")

    with st.sidebar:
        st.header("Sample Emails")
        samples = load_sample_emails()
        if samples:
            sample_options = {f"{s['id']} — {s['subject']}": s["email"] for s in samples}
            selected = st.selectbox("Load a sample email:", [""] + list(sample_options.keys()))
            if selected and st.button("Load Selected"):
                st.session_state["email_input"] = sample_options[selected]
                st.rerun()

        st.markdown("---")
        st.markdown(
            "**How it works:**\n"
            "1. Paste or load a customer email\n"
            "2. Click 'Triage Email'\n"
            "3. Review classification + suggested replies\n\n"
            "Emails are processed by Gemma 3 27B with "
            "Pydantic validation."
        )

    email_text = st.text_area(
        "Customer Email",
        value=st.session_state.get("email_input", ""),
        height=200,
        placeholder="Paste a customer email here...\n\u0623\u0648 \u0627\u0644\u0635\u0642 \u0625\u064a\u0645\u064a\u0644 \u0627\u0644\u0639\u0645\u064a\u0644 \u0647\u0646\u0627...",
    )

    if st.button("Triage Email", type="primary", disabled=not email_text.strip()):
        with st.spinner("Analyzing email..."):
            try:
                result = triage_email(email_text.strip())
                render_results(result)
            except RuntimeError as e:
                st.error(f"API Error: {e}")
            except Exception as e:
                st.error(f"Unexpected error: {e}")


if __name__ == "__main__":
    main()
