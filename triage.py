import json
import os
from pathlib import Path

import google.generativeai as genai
from dotenv import load_dotenv
from langdetect import detect, LangDetectException

from schema import TriageOutput

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise EnvironmentError(
        "GEMINI_API_KEY not found. Create a .env file in the project root with:\n"
        "GEMINI_API_KEY=your_key_here\n"
        "Get a key at https://aistudio.google.com/apikey"
    )

genai.configure(api_key=GEMINI_API_KEY)

PROMPTS_DIR = Path(__file__).parent / "prompts"
MODEL_NAME = "gemma-3-27b-it"
TEMPERATURE = 0.2


def load_prompt():
    prompt_path = PROMPTS_DIR / "system_prompt.txt"
    return prompt_path.read_text(encoding="utf-8")


def detect_language(text: str) -> str:
    try:
        lang = detect(text)
        if lang == "ar":
            return "ar"
        elif lang == "en":
            return "en"
        else:
            return "unknown"
    except LangDetectException:
        return "unknown"


def triage_email(email_text: str) -> TriageOutput:
    system_prompt = load_prompt()

    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        generation_config=genai.GenerationConfig(
            temperature=TEMPERATURE,
        ),
    )

    try:
        prompt = f"{system_prompt}\n\nEmail to classify:\n{email_text}"
        response = model.generate_content(prompt)
    except Exception as e:
        raise RuntimeError(f"Gemini API error: {e}") from e

    try:
        raw = response.text.strip()
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1].rsplit("```", 1)[0].strip()

        data = json.loads(raw)
        result = TriageOutput(**data)
        return result

    except (json.JSONDecodeError, Exception) as e:
        detected_lang = detect_language(email_text)
        return TriageOutput(
            intent="other",
            urgency="medium",
            confidence=0.0,
            language_detected=detected_lang,
            suggested_reply_en=None,
            suggested_reply_ar=None,
            escalate=True,
            reasoning=f"Schema validation failed: {e}",
            model_version=MODEL_NAME,
        )
