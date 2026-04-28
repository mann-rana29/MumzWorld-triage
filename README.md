# Mumzworld CS Email Triage

An AI-powered tool that classifies customer service emails for Mumzworld (Middle East's largest mom & baby e-commerce platform). It detects intent, urgency, and generates bilingual replies in English and Arabic.

## Features

- Classifies emails into 6 intent categories (refund, delivery, product query, complaint, exchange, other)
- Detects urgency level (high / medium / low)
- Generates suggested replies in both English and Gulf Arabic
- Auto-escalates low-confidence or high-urgency complaints to human agents
- Supports English, Arabic, and mixed-language emails
- Streamlit UI with sample email loader

## Tech Stack

- Python 3.11+
- Google Gemma 3 27B (via google-generativeai SDK)
- Pydantic v2 for response validation
- Streamlit for the UI
- langdetect for language detection
- pytest for testing

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Add your API key

Create a `.env` file in the project root:

```
GEMINI_API_KEY=your_key_here
```

Get a free key at https://aistudio.google.com/apikey

### 3. Run the app

```bash
streamlit run app.py
```

### 4. Run evals

```bash
python evals/run_evals.py
```

## Project Structure

```
mumzworld-cs-triage/
├── app.py                  # Streamlit UI
├── triage.py               # Core triage logic (Gemma API call + parsing)
├── schema.py               # Pydantic models and validation
├── prompts/
│   └── system_prompt.txt   # System prompt with few-shot examples
├── data/
│   └── sample_emails.json  # 20 sample emails for demo
├── evals/
│   ├── test_cases.json     # 5 test cases
│   └── run_evals.py        # Eval runner with scoring
├── requirements.txt
└── .env                    # API key (not committed)
```

## How It Works

1. User pastes a customer email into the Streamlit UI
2. The email is sent to Gemma 3 27B along with a system prompt that defines the classification rules
3. The model returns a JSON response with intent, urgency, confidence, and suggested replies
4. Pydantic validates the response and enforces escalation rules (e.g., low confidence = escalate, high urgency complaint = escalate)
5. Results are displayed in the UI with color-coded badges and reply columns
