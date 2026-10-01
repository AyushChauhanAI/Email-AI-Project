from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from config import GMAIL_USER, GMAIL_APP_PASSWORD
from service.email_fetcher import fetch_latest_emails
from service.intent_extractor import extract_intent

router = APIRouter(prefix="/api", tags=["Email Processing"])


class ProcessRequest(BaseModel):
    num_emails: int = Field(..., gt=0, le=20, description="Kitni latest mails process karni hain")


@router.post("/process-emails")
async def process_emails(data: ProcessRequest):
    try:
        emails = fetch_latest_emails(data.num_emails, GMAIL_USER, GMAIL_APP_PASSWORD)

        results = []
        for mail in emails:
            parsed = extract_intent(mail["body"])
            parsed["headers"] = mail["headers"]
            results.append(parsed)

        return {
            "status": "success",
            "emails_processed": len(results),
            "results": results,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))