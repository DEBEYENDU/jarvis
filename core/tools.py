from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pydantic import BaseModel, Field


class CalendarEvent(BaseModel):
    id: str
    summary: str
    start: datetime
    end: datetime


class CheckGoogleCalendarInput(BaseModel):
    days_ahead: int = Field(default=1, ge=0, le=30)


async def check_google_calendar(days_ahead: int = 1) -> dict[str, Any]:
    """
    Fetch upcoming Google Calendar events for the next N days.

    Returns a structured summary of events for LLM context.
    """
    # Actual implementation would use googleapiclient with service account / OAuth.
    # Placeholder returns empty list with proper shape for now.
    now = datetime.utcnow()
    window_end = now + timedelta(days=days_ahead)

    events: list[CalendarEvent] = []
    # TODO: integrate with real Calendar API
    return {
        "query_days": days_ahead,
        "window_start": now.isoformat(),
        "window_end": window_end.isoformat(),
        "events": [e.model_dump() for e in events],
        "count": len(events),
    }


class SendSmsSummaryInput(BaseModel):
    to_number: str
    message: str


async def send_sms_summary_to_me(to_number: str | None = None, message: str = "") -> dict[str, Any]:
    """
    Send an SMS summary to the owner via Twilio.

    Returns Twilio message SID on success.
    """
    from config import get_settings
    from twilio.rest import Client

    settings = get_settings()
    if not settings.has_twilio or not settings.twilio_phone_number:
        raise RuntimeError("Twilio credentials not configured")

    client = Client(
        settings.twilio_account_sid.get_secret_value(),
        settings.twilio_auth_token.get_secret_value(),
    )
    target = to_number or settings.sms_owner_number
    if not target:
        raise ValueError("Destination phone number not provided")

    msg = client.messages.create(
        body=message[:1600],
        from_=settings.twilio_phone_number,
        to=target,
    )
    return {
        "sid": msg.sid,
        "status": msg.status,
        "to": target,
    }


class FetchRecentNotesInput(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)


async def fetch_recent_notes(limit: int = 10) -> dict[str, Any]:
    """
    Fetch recent notes from local store.

    Returns a list of note dicts with id, title, created_at, excerpt.
    """
    # Real implementation would query SQLite / markdown store.
    now = datetime.utcnow()
    notes = [
        {
            "id": f"note-{i}",
            "title": f"Sample Note {i}",
            "created_at": (now - timedelta(days=i)).isoformat(),
            "excerpt": "Placeholder content for recent notes retrieval.",
        }
        for i in range(1, limit + 1)
    ]
    return {"notes": notes, "count": len(notes)}
