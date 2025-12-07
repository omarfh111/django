import os
import django
from fastmcp import FastMCP
from asgiref.sync import sync_to_async

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "confsite.settings")
django.setup()

from ConferenceApp.models import Conference
from SessionApp.models import Session

mcp = FastMCP("Conference Assistant")

@mcp.tool()
async def list_conferences() -> str:
    """Return all conferences with date range"""
    @sync_to_async
    def _db():
        return list(Conference.objects.all())

    conferences = await _db()
    if not conferences:
        return "No conferences found."

    return "\n".join(
        f"• {c.name} ({c.start_date} → {c.end_date})"
        for c in conferences
    )


@mcp.tool()
async def get_conference_details(name: str) -> str:
    """Return details about a given conference."""
    @sync_to_async
    def _db():
        try:
            return Conference.objects.get(name__icontains=name)
        except Conference.DoesNotExist:
            return None
        except Conference.MultipleObjectsReturned:
            return "MULTIPLE"

    c = await _db()

    if c == "MULTIPLE":
        return f"Multiple conferences found for '{name}', refine your search."

    if not c:
        return f"No conference found named '{name}'."

    return (
        f" {c.name}\n"
        f"Theme: {c.get_theme_display()}\n"
        f"Location: {c.location}\n"
        f"Dates: {c.start_date} → {c.end_date}\n"
        f"Description: {c.description}"
    )


@mcp.tool()
async def list_sessions(conference_name: str) -> str:
    """List all sessions for a conference."""
    @sync_to_async
    def _db():
        try:
            conf = Conference.objects.get(name__icontains=conference_name)
            return list(conf.sessions.all()), conf
        except Conference.DoesNotExist:
            return None, None
        except Conference.MultipleObjectsReturned:
            return "MULTIPLE", None

    sessions, conf = await _db()

    if sessions == "MULTIPLE":
        return f"More than one conference matches '{conference_name}'."

    if conf is None:
        return f"No conference '{conference_name}' found."

    if not sessions:
        return f"No sessions found for {conf.name}."

    return "\n".join(
        f"• {s.title} ({s.start_time}–{s.end_time}) – {s.room}\n  Topic: {s.topic}"
        for s in sessions
    )


@mcp.tool()
async def filter_by_theme(theme: str) -> str:
    """Filter conferences by theme loosely (case-insensitive, normalized)."""
    import unicodedata, re

    def normalize(t):
        t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode()
        return re.sub(r'[^a-z0-9 ]', '', t.lower())

    @sync_to_async
    def _db_get():
        return list(Conference.objects.all())

    conferences = await _db_get()
    theme_norm = normalize(theme)

    matches = [
        c for c in conferences
        if theme_norm in normalize(c.get_theme_display())
    ]

    if not matches:
        return f"No conferences found with theme '{theme}'."

    return "\n".join(
        f"• {c.name} ({c.start_date} → {c.end_date}) — {c.get_theme_display()}"
        for c in matches
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
