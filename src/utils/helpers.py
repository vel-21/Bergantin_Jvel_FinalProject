"""
helpers.py — ChronoVault
========================
Stateless utility functions used across the application for input
validation, date parsing, and data formatting. Keeps validation logic
out of both the models and the CLI controller.
"""

from datetime import datetime
from typing import Optional


def parse_unlock_date(date_str: str) -> Optional[str]:
    """
    Parse and validate a user-supplied date string in YYYY-MM-DD format,
    converting it to an ISO 8601 datetime string at midnight.

    Args:
        date_str (str): Raw date string from user input.

    Returns:
        str | None: ISO-format datetime string, or None if invalid.
    """
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return dt.isoformat()
    except ValueError:
        return None


def is_future_date(date_str: str) -> bool:
    """
    Determine whether a date string (YYYY-MM-DD) represents a date
    strictly in the future relative to the current moment.

    Args:
        date_str (str): Date string to validate.

    Returns:
        bool: True if the date is in the future.
    """
    try:
        dt = datetime.strptime(date_str.strip(), "%Y-%m-%d")
        return dt > datetime.now()
    except ValueError:
        return False


def validate_mood(mood_str: str) -> Optional[int]:
    """
    Validate and convert a mood string to an integer in the range [1, 5].

    Args:
        mood_str (str): Raw mood input from the user.

    Returns:
        int | None: Valid mood integer, or None if out of range or non-numeric.
    """
    try:
        mood = int(mood_str.strip())
        return mood if 1 <= mood <= 5 else None
    except ValueError:
        return None


def parse_tags(tags_str: str) -> list:
    """
    Convert a comma-separated tag string into a cleaned list of lowercase tags.

    Empty tokens and leading/trailing whitespace are discarded.

    Args:
        tags_str (str): Raw comma-separated input (e.g. "life, goals, 2025").

    Returns:
        list[str]: Cleaned list of tag strings. Empty list if input is empty.
    """
    if not tags_str.strip():
        return []
    return [tag.strip().lower() for tag in tags_str.split(",") if tag.strip()]


def format_date_friendly(iso_str: str) -> str:
    """
    Convert an ISO date string to a human-readable format.

    Args:
        iso_str (str): ISO-format date or datetime string.

    Returns:
        str: Formatted string like "January 01, 2026".
    """
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%B %d, %Y")
    except ValueError:
        return iso_str


def export_capsule_to_text(capsule) -> str:
    """
    Render an unlocked capsule as a plain-text string suitable for
    saving or copying outside the application.

    Args:
        capsule (Capsule): An unlocked Capsule object.

    Returns:
        str: Formatted text representation of the capsule.
    """
    mood_label, _, mood_icon = capsule.get_mood_display()
    return (
        f"╔══ CHRONOVAULT EXPORT ══════════════════════════╗\n"
        f"  Capsule ID : {capsule.capsule_id}\n"
        f"  Title      : {capsule.title}\n"
        f"  Created    : {format_date_friendly(capsule.created_at)}\n"
        f"  Unlocked   : {format_date_friendly(capsule.unlock_date)}\n"
        f"  Mood       : {mood_icon} {mood_label}\n"
        f"  Tags       : {', '.join(sorted(capsule.tags)) or 'none'}\n"
        f"╠══ MESSAGE ═════════════════════════════════════╣\n"
        f"{capsule.content}\n"
        f"╚════════════════════════════════════════════════╝\n"
    )
