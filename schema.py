from typing import Literal, Optional
from pydantic import BaseModel, Field, model_validator

VALID_INTENTS = Literal[
    "refund_request",
    "delivery_issue",
    "product_query",
    "complaint",
    "exchange_request",
    "other",
]

VALID_URGENCY = Literal["high", "medium", "low"]
VALID_LANGUAGE = Literal["en", "ar", "mixed", "unknown"]
MODEL_VERSION = "gemma-3-27b-it"


class TriageOutput(BaseModel):
    intent: VALID_INTENTS
    urgency: VALID_URGENCY
    confidence: float = Field(ge=0.0, le=1.0)
    language_detected: VALID_LANGUAGE
    suggested_reply_en: Optional[str] = None
    suggested_reply_ar: Optional[str] = None
    escalate: bool
    reasoning: str
    model_version: str = MODEL_VERSION

    @model_validator(mode="after")
    def validate_escalation_rules(self):
        if self.confidence < 0.6:
            self.escalate = True

        if self.urgency == "high" and self.intent == "complaint":
            self.escalate = True

        if self.escalate:
            self.suggested_reply_en = None
            self.suggested_reply_ar = None

        if self.confidence < 0.6:
            self.suggested_reply_en = None
            self.suggested_reply_ar = None

        self.confidence = round(self.confidence, 2)

        return self
