# Mumzworld CS Triage - Project Q&A & Loom Script

This document contains potential interview questions (both general technical and specifically for Mumzworld recruiters) as well as a script for recording a Loom video demonstration.

---

## Part 1: Mumzworld Recruiter Interview Questions

If you are interviewing with someone from Mumzworld (HR, Engineering Manager, or Product Manager), they will care less about "how" you coded it and more about **business impact, customer empathy, and scalability**.

### 1. How does this tool actually save our operations team money/time?
**Question:** "What's the ROI of this tool for our CS team?"
**Answer:** "Right now, your team reads every single email just to figure out who should handle it. This tool automates the 'triage' step. By instantly tagging an email with its intent and urgency, we can route simple 'where is my order' tickets to junior agents or auto-replies, and instantly send high-urgency issues (like missing baby formula) to senior agents. It cuts response time and saves thousands of manual hours per week."

### 2. Why is the Arabic dialect so important here?
**Question:** "I noticed you focused on Gulf Arabic instead of Modern Standard Arabic (MSA). Why?"
**Answer:** "Mumzworld is a brand that parents trust. If an angry mother in Riyadh emails you about a broken stroller, and an AI replies in rigid, robotic MSA, she's going to feel like the company doesn't care. By explicitly prompting the model to use conversational Khaleeji (Gulf) Arabic, the auto-generated replies feel warm, empathetic, and human, which protects the brand's reputation."

### 3. How do we prevent the AI from making things worse with angry customers?
**Question:** "AI can sometimes hallucinate or give bad answers. How do we trust this not to anger our customers further?"
**Answer:** "That's exactly why I built the **escalation logic**. The system isn't designed to answer everything. If the AI detects that an email is highly urgent, or if it has low confidence in its own answer, it automatically trips the `escalate: True` flag and suppresses the auto-reply. The AI knows when to step back and let a real human take over."

### 4. How would you put this into production at Mumzworld?
**Question:** "This is a great Streamlit prototype, but we use Zendesk (or Freshdesk). How do we integrate this?"
**Answer:** "The Streamlit UI is just for the demo. The core logic in `triage.py` can be deployed as an AWS Lambda function or a FastAPI microservice. We would set up a webhook in Zendesk so that every time a new ticket arrives, it pings the microservice. The service returns the JSON tags, and Zendesk automatically applies those tags and routes the ticket."

### 5. Why did you use Gemma 3 instead of building a custom classification model?
**Question:** "We have a lot of data. Why use a generalized LLM instead of a specialized NLP model?"
**Answer:** "A specialized model is great for simple classification, but it requires constant retraining as your products change, and it can't generate localized Arabic replies. Gemma 3 handles the Arabic/English code-switching perfectly right out of the box. However, if I joined the team, my next step would be to fine-tune a smaller, cheaper open-source model specifically on Mumzworld's historical ticket data to reduce API costs."

---

## Part 2: Academic & General Technical Q&A

These are questions a professor, TA, or general technical interviewer might ask.

### 1. What does this project do and what problem does it solve?
**Answer:** "This project is an AI-powered email triage system for an e-commerce platform. It automates the process of reading emails, identifying the intent, calculating an urgency level, and generating a draft reply in English or Arabic. It saves time by filtering the easy tickets so humans can focus on the hard ones."

### 2. Why did you choose Google's Gemma model?
**Answer:** "I chose Gemma because it's available for free through the Google AI Studio API. It's also very capable of understanding both English and Arabic. A smaller local model might struggle with the mixed languages and dialects, and GPT-4 would require paid API credits."

### 3. What is Pydantic and why did you use it?
**Answer:** "Pydantic strictly enforces the data structure. If you just use standard JSON parsing, the AI might hallucinate a key that doesn't exist, which could crash the app. If the model returns something invalid, Pydantic catches it immediately, and I can handle the error gracefully by falling back to a safe 'escalate' state."

### 4. How does the auto-escalation logic work?
**Answer:** "There are two main rules built into the Pydantic schema validator. First, if the AI's confidence score is below 60%, it automatically escalates it. Second, if the urgency is 'high' and the intent is a 'complaint', it escalates it immediately, because angry customers need human empathy, not an AI bot."

### 5. What did your evaluation script measure?
**Answer:** "I wrote `run_evals.py` to test 15 different emails. The script checks three things: did it get the intent right, the urgency right, and did it correctly decide whether to escalate? It scores the run out of 100% and fails the test if the overall score drops below 70%."

---

## Part 3: Loom Video Recording Script

Keep the video under **3 minutes**. Be energetic, clear, and focus on the **value** of what you built.

### Section 1: The Hook & The Problem (0:00 - 0:30)
*(Screen showing the Mumzworld website or the Streamlit app homepage)*
**You:** "Hi! I'm [Your Name]. I built an AI-powered customer service triage system specifically designed for Mumzworld's operations team. 
Currently, e-commerce CS teams spend countless hours just reading emails to figure out what the customer wants, especially in the GCC where customers mix English, Arabic, and Arabizi in the same sentence. My tool completely automates that first step."

### Section 2: The Live Demo (0:30 - 1:30)
*(Screen showing the Streamlit app. Open the sidebar and select an Arabic complaint email, like "التوصيل متأخر وايد" (Delivery very late) or sample_012 (Furious complaint))*
**You:** "Let me show you how it works. Here's a real-world example of an angry customer complaining about a delayed baby formula delivery in Arabic. I click 'Triage Email'.
*(Wait for it to load)*
Notice what happens. The system instantly tags it as a 'Delivery Issue' with 'High' urgency. But more importantly, look at the yellow warning banner. The system realized this is a high-urgency issue concerning a baby's health, so it automatically flagged it for **Human Escalation** and suppressed the auto-reply. We don't want an AI talking to an angry mother; we want a human to step in."

### Section 3: The Architecture (1:30 - 2:15)
*(Screen showing `schema.py` and `triage.py` code in your editor)*
**You:** "Under the hood, this uses Google's Gemma 3 model. But the most important part of the code isn't the AI, it's the validation. 
In my `schema.py` file, I used Pydantic to enforce strict business rules. If the AI's confidence drops below 60%, or if it's a high-urgency complaint, the code forces an escalation. This prevents the AI from going rogue and ensures safe, predictable outputs."

### Section 4: The Impact / Outro (2:15 - 2:45)
*(Screen back to the Streamlit app showing a successful refund auto-reply)*
**You:** "I also specifically prompted the model to generate Arabic replies in conversational Gulf Arabic, not rigid Modern Standard Arabic, so it actually sounds like a real Mumzworld agent.
Ultimately, this tool can easily be connected to Zendesk or Freshdesk via a webhook, saving thousands of manual routing hours and bringing down resolution times for parents across the Middle East. Thanks for watching!"
