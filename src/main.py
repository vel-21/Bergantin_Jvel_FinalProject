"""
main.py — ChronoVault
=====================
Entry point and primary CLI controller for ChronoVault: a time-locked
digital capsule system where users seal messages to their future selves.

Run with:
    python src/main.py

Author : [Your Name]
Course : Intermediate Programming
"""

import os
import sys

# Ensure imports resolve correctly when run from project root or src/
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models.vault import Vault
from utils.display import (
    clear, print_banner, print_menu, print_divider,
    format_capsule_card, format_stats, format_timeline,
    prompt, print_success, print_error, print_info, print_warning, pause,
)
from utils.helpers import (
    parse_unlock_date, is_future_date, validate_mood,
    parse_tags, format_date_friendly, export_capsule_to_text,
)


class ChronoVaultApp:
    """
    Primary application controller for the ChronoVault CLI.

    Orchestrates the menu loop, delegates to Vault for data operations,
    and uses display/helper utilities for all I/O.

    Attributes:
        vault (Vault): The central capsule repository.
    """

    def __init__(self):
        """Initialize the app and load the Vault from disk."""
        data_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "vault.json",
        )
        self.vault = Vault(data_path=data_path)

    # ──────────────────────────────────────────────
    # Main Loop
    # ──────────────────────────────────────────────

    def run(self) -> None:
        """Launch the application and begin the main menu loop."""
        clear()
        print_banner()
        count = self.vault.total_count()
        unlocked = self.vault.unlocked_count()
        print_info(
            f"Vault ready — {count} capsule(s) stored, "
            f"{unlocked} unlocked and awaiting you."
        )

        while True:
            self._main_menu()

    def _main_menu(self) -> None:
        """Display the main navigation menu and dispatch user choices."""
        options = [
            "Seal a New Capsule       ✉️",
            "View All Capsules        📂",
            "Open a Capsule           🔓",
            "Search Capsules          🔍",
            "Browse by Tag            🏷️",
            "Mood Analytics           📊",
            "Timeline View            🕰️",
            "Export a Capsule         💾",
            "Delete a Capsule         🗑️",
            "Exit                     👋",
        ]
        print_menu("✦  C H R O N O V A U L T  ✦", options)

        # Dispatch table: maps choice string -> handler method
        actions = {
            "1": self._create_capsule,
            "2": self._view_all,
            "3": self._open_capsule,
            "4": self._search_capsules,
            "5": self._browse_by_tag,
            "6": self._mood_analytics,
            "7": self._timeline_view,
            "8": self._export_capsule,
            "9": self._delete_capsule,
            "10": self._exit,
        }

        choice = prompt("Choose an option")
        action = actions.get(choice)
        if action:
            action()
        else:
            print_error("Invalid choice — please enter a number between 1 and 10.")
            pause()

    # ──────────────────────────────────────────────
    # 1. Create Capsule
    # ──────────────────────────────────────────────

    def _create_capsule(self) -> None:
        """
        Multi-step wizard for sealing a new time-locked capsule.

        Gathers title, multi-line message content, unlock date, mood,
        tags, and an optional password, then delegates to the Vault.
        """
        print("\n  ✉️   SEAL A NEW CAPSULE")
        print_divider()

        # ── Step 1: Title ──
        title = prompt("Capsule title")
        if not title:
            print_error("Title cannot be empty.")
            pause()
            return

        # ── Step 2: Multi-line message ──
        print("\n  📝  Write your message. Type END on its own line when done.")
        print("  " + "─" * 50)
        lines = []
        while True:
            line = input("     > ")
            if line.strip().upper() == "END":
                break
            lines.append(line)
        content = "\n".join(lines).strip()
        if not content:
            print_error("Message cannot be empty.")
            pause()
            return

        # ── Step 3: Unlock date ──
        print_info("The capsule will be sealed until this date.")
        while True:
            date_str = prompt("Unlock date (YYYY-MM-DD)")
            if not is_future_date(date_str):
                print_error("Please enter a valid date in the future (YYYY-MM-DD).")
            else:
                unlock_date = parse_unlock_date(date_str)
                break

        # ── Step 4: Mood ──
        print("\n  🌡️   How are you feeling right now?")
        print("       [1] 😞 Terrible  [2] 😕 Bad  [3] 😐 Neutral  [4] 🙂 Good  [5] 😄 Amazing")
        while True:
            mood = validate_mood(prompt("Mood (1–5)"))
            if mood:
                break
            print_error("Enter a number between 1 and 5.")

        # ── Step 5: Tags ──
        tags_raw = prompt("Tags (comma-separated, e.g. life,future,goals) or Enter to skip")
        tags = parse_tags(tags_raw)

        # ── Step 6: Password ──
        password = None
        use_pw = prompt("Password-protect this capsule? (y/n)").lower()
        if use_pw == "y":
            pw1 = prompt("Set a password")
            pw2 = prompt("Confirm password")
            if pw1 != pw2:
                print_warning("Passwords did not match — capsule created without password.")
            elif not pw1:
                print_warning("Password cannot be empty — skipping.")
            else:
                password = pw1

        # ── Create ──
        capsule = self.vault.create_capsule(title, content, unlock_date, mood, tags, password)
        days = capsule.days_remaining()
        print_success(f"Capsule #{capsule.capsule_id} has been sealed!")
        print_info(f"It will unlock on {format_date_friendly(unlock_date)} ({days} day(s) from now). 🕰️")
        pause()

    # ──────────────────────────────────────────────
    # 2. View All
    # ──────────────────────────────────────────────

    def _view_all(self) -> None:
        """Display all capsules sorted by a user-selected field."""
        if self.vault.total_count() == 0:
            print_info("Your vault is empty! Seal your first capsule to get started.")
            pause()
            return

        print("\n  📂  ALL CAPSULES")
        print_divider()
        print_info(
            f"Total: {self.vault.total_count()}  │  "
            f"🔒 Locked: {self.vault.locked_count()}  │  "
            f"🔓 Unlocked: {self.vault.unlocked_count()}"
        )

        print("\n  Sort by:  [1] Unlock Date  [2] Creation Date  [3] Mood  [4] Title")
        sort_map = {"1": "unlock_date", "2": "created_at", "3": "mood", "4": "title"}
        key = sort_map.get(prompt("Sort option (default: 1)"), "unlock_date")

        rev_input = prompt("Descending order? (y/n, default: n)").lower()
        reverse = rev_input == "y"

        print()
        for capsule in self.vault.get_sorted(key=key, reverse=reverse):
            print(format_capsule_card(capsule))

        pause()

    # ──────────────────────────────────────────────
    # 3. Open Capsule
    # ──────────────────────────────────────────────

    def _open_capsule(self) -> None:
        """
        Open and read a single capsule by ID.

        Checks unlock status, handles password verification,
        and marks the capsule as read on first open.
        """
        capsule_id = prompt("Enter Capsule ID").upper()
        capsule = self.vault.get_capsule(capsule_id)

        if not capsule:
            print_error(f"No capsule found with ID '{capsule_id}'.")
            pause()
            return

        if not capsule.is_unlocked():
            days = capsule.days_remaining()
            print_error(
                f"⏳ This capsule is still sealed for {days} more day(s). "
                f"Come back on {format_date_friendly(capsule.unlock_date)}."
            )
            pause()
            return

        if capsule.password_hash:
            pw = prompt("🔑 This capsule is password-protected. Enter password")
            if not capsule.verify_password(pw):
                print_error("Incorrect password. Access denied.")
                pause()
                return

        # Mark as opened and persist
        if not capsule.is_opened:
            capsule.is_opened = True
            self.vault._save()
            print_info("📬 First time opening this capsule!")

        print()
        print(format_capsule_card(capsule, show_content=True))
        pause()

    # ──────────────────────────────────────────────
    # 4. Search
    # ──────────────────────────────────────────────

    def _search_capsules(self) -> None:
        """Full-text search across unlocked capsule titles, content, and tags."""
        query = prompt("Search query")
        if not query:
            print_error("Query cannot be empty.")
            pause()
            return

        results = self.vault.search(query)
        if not results:
            print_info(f"No unlocked capsules matched '{query}'.")
        else:
            print_success(f"Found {len(results)} result(s) for '{query}':")
            for capsule in results:
                print(format_capsule_card(capsule))

        pause()

    # ──────────────────────────────────────────────
    # 5. Browse by Tag
    # ──────────────────────────────────────────────

    def _browse_by_tag(self) -> None:
        """List all tags and filter capsules by a selected tag."""
        all_tags = self.vault.get_all_tags()
        if not all_tags:
            print_info("No tags found in the vault yet.")
            pause()
            return

        print("\n  🏷️   AVAILABLE TAGS")
        print_divider()
        sorted_tags = sorted(all_tags)
        print("  " + "  ".join(f"#{t}" for t in sorted_tags))

        tag = prompt("Enter a tag to browse")
        results = self.vault.filter_by_tag(tag)

        if not results:
            print_info(f"No capsules found with tag '#{tag}'.")
        else:
            print_success(f"Capsules tagged '#{tag}' ({len(results)} found):")
            for capsule in results:
                print(format_capsule_card(capsule))

        pause()

    # ──────────────────────────────────────────────
    # 6. Mood Analytics
    # ──────────────────────────────────────────────

    def _mood_analytics(self) -> None:
        """Display an ASCII mood distribution chart from unlocked capsules."""
        print("\n  📊  MOOD ANALYTICS")
        print_divider()
        stats = self.vault.get_mood_stats()
        print(format_stats(stats))

        if stats:
            filter_input = prompt("Filter unlocked capsules by mood (1–5) or Enter to skip")
            if filter_input:
                mood = validate_mood(filter_input)
                if mood:
                    filtered = self.vault.filter_by_mood(mood)
                    print_success(f"Capsules with mood {mood}: {len(filtered)} found")
                    for c in filtered:
                        print(format_capsule_card(c))
                else:
                    print_error("Invalid mood value.")

        pause()

    # ──────────────────────────────────────────────
    # 7. Timeline View
    # ──────────────────────────────────────────────

    def _timeline_view(self) -> None:
        """Show a chronological creation timeline of all capsules."""
        print("\n  🕰️   CREATION TIMELINE")
        print_divider()
        events = self.vault.get_timeline()
        from utils.display import format_timeline
        print(format_timeline(events))
        pause()

    # ──────────────────────────────────────────────
    # 8. Export Capsule
    # ──────────────────────────────────────────────

    def _export_capsule(self) -> None:
        """Export an unlocked capsule to a plain-text file in data/exports/."""
        capsule_id = prompt("Enter Capsule ID to export").upper()
        capsule = self.vault.get_capsule(capsule_id)

        if not capsule:
            print_error(f"No capsule found with ID '{capsule_id}'.")
            pause()
            return

        if not capsule.is_unlocked():
            print_error("Cannot export a locked capsule.")
            pause()
            return

        if capsule.password_hash:
            pw = prompt("Enter password to export")
            if not capsule.verify_password(pw):
                print_error("Incorrect password.")
                pause()
                return

        export_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data", "exports",
        )
        os.makedirs(export_dir, exist_ok=True)
        filename = os.path.join(export_dir, f"capsule_{capsule.capsule_id}.txt")

        # Context manager for file writing (advanced Python concept)
        with open(filename, "w", encoding="utf-8") as f:
            f.write(export_capsule_to_text(capsule))

        print_success(f"Capsule exported to: {filename}")
        pause()

    # ──────────────────────────────────────────────
    # 9. Delete Capsule
    # ──────────────────────────────────────────────

    def _delete_capsule(self) -> None:
        """Permanently delete a capsule after explicit user confirmation."""
        capsule_id = prompt("Enter Capsule ID to delete").upper()
        capsule = self.vault.get_capsule(capsule_id)

        if not capsule:
            print_error(f"No capsule found with ID '{capsule_id}'.")
            pause()
            return

        print_warning(f"You are about to permanently delete: '{capsule.title}'")
        confirm = prompt("Type YES to confirm deletion")
        if confirm.strip().upper() == "YES":
            self.vault.delete_capsule(capsule_id)
            print_success("Capsule permanently removed from the vault.")
        else:
            print_info("Deletion cancelled.")

        pause()

    # ──────────────────────────────────────────────
    # 10. Exit
    # ──────────────────────────────────────────────

    def _exit(self) -> None:
        """Display a farewell message and terminate the application."""
        print("\n  👋  Thank you for using ChronoVault.")
        print("      Time is precious — seal it wisely. 🕰️\n")
        sys.exit(0)


# ──────────────────────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app = ChronoVaultApp()
    app.run()
