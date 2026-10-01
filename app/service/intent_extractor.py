"""
service/intent_extractor.py

Groq LLM ka use karke email body se structured "intent" extract karta hai.
Router (connection_api.py) is function ko call karta hai aur output mein
headers merge karke response return karta hai.
"""

import json
import logging

from groq import Groq

from config import GROQ_API_KEY

logger = logging.getLogger(__name__)

# Groq client ek baar initialize karke reuse karenge
client = Groq(api_key=GROQ_API_KEY)

# Model yahan se change kar sakte ho agar zaroorat pade
GROQ_MODEL = "openai/gpt-oss-120b"

SYSTEM_PROMPT = """You are an assistant that reads an email body and extracts its intent.

Return ONLY a valid JSON object (no markdown, no commentary) with this exact schema:
{
  "intent": string,            // one of: "job_opportunity", "client_inquiry", "meeting_request", "follow_up", "payment", "spam", "other"
  "summary": string,           // 1-2 sentence plain-language summary of the email
  "urgency": string,           // one of: "low", "medium", "high"
  "action_required": boolean,  // true if the recipient needs to respond or act
  "key_entities": {
    "sender_name": string | null,
    "company": string | null,
    "deadline": string | null,   // ISO date if mentioned, else null
    "budget": string | null      // amount/range if mentioned, else null
  }
}

If a field cannot be determined, use null (or false/"low" for booleans/urgency as appropriate).
Do not invent information that is not present in the email."""


def _empty_result(reason: str) -> dict:
    """Jab email body khali ho ya kuch fail ho jaaye, tab default shape return karta hai."""
    return {
        "intent": "unknown",
        "summary": "",
        "urgency": "low",
        "action_required": False,
        "key_entities": {
            "sender_name": None,
            "company": None,
            "deadline": None,
            "budget": None,
        },
        "error": reason,
    }


def extract_intent(email_body: str) -> dict:
    """
    Email body ko Groq LLM ko bhejta hai aur structured intent JSON return karta hai.
    Router isi dict mein "headers" key add karke final response banata hai.
    """
    if not email_body or not email_body.strip():
        return _empty_result("Email body khali tha, kuch extract nahi kiya ja saka.")

    # Bahut lambi body ko truncate karein taaki token limit cross na ho
    truncated_body = email_body.strip()[:6000]

    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Email body:\n\n{truncated_body}"},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
        )

        raw_content = response.choices[0].message.content
        parsed = json.loads(raw_content)

        # Basic shape validation - agar koi expected key missing hai to default fill karein
        parsed.setdefault("intent", "unknown")
        parsed.setdefault("summary", "")
        parsed.setdefault("urgency", "low")
        parsed.setdefault("action_required", False)
        parsed.setdefault(
            "key_entities",
            {"sender_name": None, "company": None, "deadline": None, "budget": None},
        )

        return parsed

    except json.JSONDecodeError as e:
        logger.error(f"Groq response ko JSON parse karne mein error: {e}")
        return _empty_result("LLM se aaya response valid JSON nahi tha.")

    except Exception as e:
        logger.error(f"Intent extraction fail hui: {e}")
        return _empty_result(f"Groq API call fail hui: {str(e)}")