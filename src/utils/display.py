"""
display.py — ChronoVault
========================
All terminal display helpers: banners, menus, capsule cards,
analytics charts, and styled prompts. Centralizes all UI output
to keep business logic separate from presentation.
"""

import os
import time
from datetime import datetime


# ──────────────────────────────────────────────────────────────
# Constants
# ──────────────────────────────────────────────────────────────

WIDTH = 58

BANNER = r"""
  ╔══════════════════════════════════════════════════════╗
  ║                                                      ║
  ║    ░█▀▀░█░█░█▀▄░█▀█░█▀█░█▀█░█░█░█▀█░█░█░█░░░▀█▀    ║
  ║    ░█░░░█▀█░█▀▄░█░█░█░█░█░█░▀▄▀░█▀█░█░█░█░░░░█░    ║
  ║    ░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░░▀░░▀░▀░▀▀▀░▀▀▀░░▀░    ║
  ║                                                      ║
  ║         ✦  Your Time-Locked Message Vault  ✦         ║
  ╚══════════════════════════════════════════════════════╝
"""

MOOD_ICONS = {1: "😞", 2: "😕", 3: "😐", 4: "🙂", 5: "😄"}


# ──────────────────────────────────────────────────────────────
# Core Display Functions
# ──────────────────────────────────────────────────────────────

def clear() -> None:
    """Clear the terminal screen cross-platform."""
    os.system("cls" if os.name == "nt" else "clear")


def print_banner() -> None:
    """Print the ChronoVault ASCII art banner."""
    print(BANNER)


def print_divider(char: str = "─", width: int = WIDTH) -> None:
    """Print a horizontal divider line."""
    print(f"  {char * width}")


def slow_print(text: str, delay: float = 0.012) -> None:
    """
    Print text with a typewriter effect character by character.

    Args:
        text (str): Text to display.
        delay (float): Seconds between each character.
    """
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


# ──────────────────────────────────────────────────────────────
# Menu System
# ──────────────────────────────────────────────────────────────

def print_menu(title: str, options: list) -> None:
    """
    Render a styled, numbered CLI menu.

    Args:
        title (str): Menu header text.
        options (list): List of option strings.
    """
    pad = (WIDTH - len(title) - 4) // 2
    print(f"\n  ╔{'═' * (WIDTH)}╗")
    print(f"  ║{' ' * pad}  {title}  {' ' * pad}║")
    print(f"  ╠{'═' * (WIDTH)}╣")
    for i, opt in enumerate(options, 1):
        line = f"  [{i}] {opt}"
        print(f"  ║  {line:<{WIDTH - 2}}║")
    print(f"  ╚{'═' * (WIDTH)}╝")


# ──────────────────────────────────────────────────────────────
# Capsule Card Renderer
# ──────────────────────────────────────────────────────────────

def format_capsule_card(capsule, show_content: bool = False) -> str:
    """
    Format a Capsule as a visual card for CLI display.

    Shows metadata (title, status, dates, mood, tags) and optionally
    renders the full content for unlocked capsules.

    Args:
        capsule (Capsule): The capsule to display.
        show_content (bool): Whether to include the message body.

    Returns:
        str: A multi-line formatted string ready to print.
    """
    mood_label, mood_bar, mood_icon = capsule.get_mood_display()
    status    = "🔓 UNLOCKED" if capsule.is_unlocked() else f"🔒 {capsule.days_remaining()} day(s) remaining"
    lock_icon = " 🔑" if capsule.password_hash else ""
    opened    = " ✔ read" if capsule.is_opened else ""
    tags_str  = ", ".join(f"#{t}" for t in sorted(capsule.tags)) if capsule.tags else "none"

    lines = [
        f"  ┌──── Capsule #{capsule.capsule_id}{lock_icon}{opened}",
        f"  │  📌 Title    : {capsule.title}",
        f"  │  ⏳ Status   : {status}",
        f"  │  📅 Created  : {capsule.created_at[:10]}",
        f"  │  🗓  Unlocks  : {capsule.unlock_date[:10]}",
        f"  │  {mood_icon} Mood     : {mood_bar} {mood_label} ({capsule.mood}/5)",
        f"  │  🏷  Tags     : {tags_str}",
    ]

    if show_content:
        lines.append(f"  │")
        lines.append(f"  │  ── Message ──────────────────────────────────")
        for line in capsule.content.split("\n"):
            lines.append(f"  │    {line}")
        lines.append(f"  │  ────────────────────────────────────────────")

    lines.append("  └─────────────────────────────────────────────────")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Analytics Display
# ──────────────────────────────────────────────────────────────

def format_stats(stats: dict | None) -> str:
    """
    Render a horizontal ASCII bar chart of mood distribution.

    Args:
        stats (dict | None): Output of Vault.get_mood_stats().

    Returns:
        str: Formatted analytics display string.
    """
    if not stats:
        return "  No unlocked capsules to analyze yet. Seal some memories first! 🕰️"

    mood_labels = {1: "Terrible", 2: "Bad", 3: "Neutral", 4: "Good", 5: "Amazing"}
    lines = [
        f"  📊  Mood Analytics  ({stats['total']} unlocked entries)",
        f"  {'─' * 46}",
        f"  Average Mood : {stats['average']} / 5.0   "
        f"{'★' * round(stats['average'])}{'☆' * (5 - round(stats['average']))}",
        f"  Highest      : {stats['highest']}/5  {MOOD_ICONS[stats['highest']]}",
        f"  Lowest       : {stats['lowest']}/5  {MOOD_ICONS[stats['lowest']]}",
        f"",
        f"  Distribution:",
        f"  {'─' * 46}",
    ]
    max_count = max(stats["distribution"].values()) or 1
    for mood_val in range(1, 6):
        count   = stats["distribution"][mood_val]
        bar_len = int((count / max_count) * 28)
        bar     = "█" * bar_len + "░" * (28 - bar_len)
        icon    = MOOD_ICONS[mood_val]
        label   = mood_labels[mood_val]
        lines.append(f"  {icon} {label:<8s} │{bar}│ {count}")

    return "\n".join(lines)


def format_timeline(events: list) -> str:
    """
    Render a simple text timeline of capsule creation events.

    Args:
        events (list): Output of Vault.get_timeline().

    Returns:
        str: A formatted timeline string.
    """
    if not events:
        return "  No events yet."
    lines = ["  🕰️  Creation Timeline", f"  {'─' * 40}"]
    for i, event in enumerate(events):
        connector = "└" if i == len(events) - 1 else "├"
        lines.append(f"  {connector}── {event['date']}  ·  {event['title']}  [{event['id']}]")
    return "\n".join(lines)


# ──────────────────────────────────────────────────────────────
# Input / Output Helpers
# ──────────────────────────────────────────────────────────────

def prompt(text: str) -> str:
    """
    Styled input prompt with a leading arrow indicator.

    Args:
        text (str): Prompt label.

    Returns:
        str: Stripped user input.
    """
    return input(f"\n  ▶ {text}: ").strip()


def print_success(msg: str) -> None:
    """Print a success message."""
    print(f"\n  ✅  {msg}")


def print_error(msg: str) -> None:
    """Print an error message."""
    print(f"\n  ❌  {msg}")


def print_info(msg: str) -> None:
    """Print an informational message."""
    print(f"\n  ℹ   {msg}")


def print_warning(msg: str) -> None:
    """Print a warning message."""
    print(f"\n  ⚠️   {msg}")


def pause() -> None:
    """Wait for the user to press Enter before continuing."""
    input("\n  [ Press Enter to continue... ]")
