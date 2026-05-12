"""
vault.py — ChronoVault
======================
Defines the Vault class, which acts as the central repository for
all Capsule objects. Handles persistence (load/save to JSON), sorting,
searching, filtering, and aggregate analytics.
"""

import json
import os
import uuid
import hashlib
from datetime import datetime
from typing import Generator, List, Optional

from models.capsule import Capsule


class Vault:
    """
    The master repository for all time-locked Capsule objects.

    Responsibilities:
        - Loading and saving capsules to a JSON file (file handling).
        - Creating, retrieving, and deleting capsules (CRUD).
        - Providing search, filter, and sort operations (algorithms).
        - Generating analytics (mood statistics, tag summaries).

    Attributes:
        data_path (str): Path to the JSON persistence file.
        capsules (dict): Mapping of capsule_id -> Capsule instance.
    """

    def __init__(self, data_path: str = "data/vault.json"):
        """
        Initialize the Vault and load existing capsules from disk.

        Args:
            data_path (str): Filesystem path for the JSON storage file.
        """
        self.data_path = data_path
        self.capsules: dict[str, Capsule] = {}
        self._load()

    # ──────────────────────────────────────────────
    # Persistence
    # ──────────────────────────────────────────────

    def _load(self) -> None:
        """
        Load capsule data from the JSON file using a context manager.
        Creates the data directory automatically if it does not exist.
        """
        os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
        if os.path.exists(self.data_path):
            with open(self.data_path, "r", encoding="utf-8") as f:
                raw = json.load(f)
                # Dict comprehension to rebuild Capsule objects from raw dicts
                self.capsules = {
                    cid: Capsule.from_dict(cdata)
                    for cid, cdata in raw.items()
                }

    def _save(self) -> None:
        """
        Persist all capsule data to the JSON file using a context manager.
        """
        with open(self.data_path, "w", encoding="utf-8") as f:
            json.dump(
                {cid: c.to_dict() for cid, c in self.capsules.items()},
                f,
                indent=2,
                ensure_ascii=False,
            )

    # ──────────────────────────────────────────────
    # CRUD Operations
    # ──────────────────────────────────────────────

    def create_capsule(
        self,
        title: str,
        content: str,
        unlock_date: str,
        mood: int = 3,
        tags: list = None,
        password: str = None,
    ) -> Capsule:
        """
        Create a new Capsule, store it in the vault, and persist to disk.

        Args:
            title (str): Title of the capsule.
            content (str): Message content to seal.
            unlock_date (str): ISO-format future unlock date.
            mood (int): Mood rating 1–5.
            tags (list, optional): List of tag strings.
            password (str, optional): Plaintext password to hash and store.

        Returns:
            Capsule: The newly created capsule instance.
        """
        capsule_id    = str(uuid.uuid4())[:8].upper()
        password_hash = hashlib.sha256(password.encode()).hexdigest() if password else None
        capsule       = Capsule(capsule_id, title, content, unlock_date, mood, tags, password_hash)
        self.capsules[capsule_id] = capsule
        self._save()
        return capsule

    def get_capsule(self, capsule_id: str) -> Optional[Capsule]:
        """
        Retrieve a single capsule by its ID (case-insensitive).

        Args:
            capsule_id (str): The capsule identifier.

        Returns:
            Capsule | None: The matching capsule, or None if not found.
        """
        return self.capsules.get(capsule_id.upper())

    def delete_capsule(self, capsule_id: str) -> bool:
        """
        Permanently remove a capsule from the vault.

        Args:
            capsule_id (str): The capsule identifier to remove.

        Returns:
            bool: True if deleted, False if not found.
        """
        if capsule_id in self.capsules:
            del self.capsules[capsule_id]
            self._save()
            return True
        return False

    # ──────────────────────────────────────────────
    # Generators (Advanced Python Concept)
    # ──────────────────────────────────────────────

    def get_unlocked(self) -> Generator[Capsule, None, None]:
        """
        Generator that lazily yields all currently unlocked capsules.

        Yields:
            Capsule: Each capsule whose unlock date has passed.
        """
        for capsule in self.capsules.values():
            if capsule.is_unlocked():
                yield capsule

    def get_locked(self) -> Generator[Capsule, None, None]:
        """
        Generator that lazily yields all still-locked capsules.

        Yields:
            Capsule: Each capsule that is not yet readable.
        """
        for capsule in self.capsules.values():
            if not capsule.is_unlocked():
                yield capsule

    # ──────────────────────────────────────────────
    # Search & Filter Algorithms
    # ──────────────────────────────────────────────

    def search(self, query: str) -> List[Capsule]:
        """
        Full-text search across unlocked capsule titles, content, and tags.

        Uses a list comprehension with multi-condition filtering.

        Args:
            query (str): The search string.

        Returns:
            list[Capsule]: Matching unlocked capsules.
        """
        q = query.lower()
        return [
            c for c in self.capsules.values()
            if c.is_unlocked() and (
                q in c.title.lower()
                or q in c.content.lower()
                or any(q in tag.lower() for tag in c.tags)
            )
        ]

    def filter_by_tag(self, tag: str) -> List[Capsule]:
        """
        Return all capsules (locked or unlocked) that contain a given tag.

        Args:
            tag (str): Tag string to match (case-insensitive).

        Returns:
            list[Capsule]: Capsules with the matching tag.
        """
        tag_lower = tag.lower()
        return [
            c for c in self.capsules.values()
            if tag_lower in {t.lower() for t in c.tags}
        ]

    def filter_by_mood(self, mood: int) -> List[Capsule]:
        """
        Return all unlocked capsules matching a specific mood value.

        Args:
            mood (int): Mood integer (1–5).

        Returns:
            list[Capsule]: Unlocked capsules with the specified mood.
        """
        return [c for c in self.get_unlocked() if c.mood == mood]

    def get_sorted(self, key: str = "unlock_date", reverse: bool = False) -> List[Capsule]:
        """
        Return all capsules sorted by a specified field.

        Implements a custom sort using a dispatch dictionary of key functions,
        making the sort strategy easily extensible.

        Args:
            key (str): Sort field — one of 'unlock_date', 'created_at', 'mood', 'title'.
            reverse (bool): If True, sort in descending order.

        Returns:
            list[Capsule]: Sorted list of all capsules.
        """
        sort_funcs = {
            "unlock_date": lambda c: c.unlock_date,
            "created_at":  lambda c: c.created_at,
            "mood":        lambda c: c.mood,
            "title":       lambda c: c.title.lower(),
        }
        func = sort_funcs.get(key, sort_funcs["unlock_date"])
        return sorted(self.capsules.values(), key=func, reverse=reverse)

    # ──────────────────────────────────────────────
    # Analytics
    # ──────────────────────────────────────────────

    def get_mood_stats(self) -> Optional[dict]:
        """
        Compute aggregate mood statistics across all unlocked capsules.

        Returns:
            dict | None: Stats dictionary with average, distribution, highs/lows;
                         None if there are no unlocked capsules.
        """
        unlocked = list(self.get_unlocked())
        if not unlocked:
            return None

        moods = [c.mood for c in unlocked]
        return {
            "average":      round(sum(moods) / len(moods), 2),
            "total":        len(unlocked),
            "distribution": {i: moods.count(i) for i in range(1, 6)},
            "highest":      max(moods),
            "lowest":       min(moods),
        }

    def get_all_tags(self) -> set:
        """
        Collect every unique tag used across all capsules.

        Uses a set comprehension to deduplicate across capsules.

        Returns:
            set: All unique tag strings.
        """
        return {tag for capsule in self.capsules.values() for tag in capsule.tags}

    def get_timeline(self) -> List[dict]:
        """
        Build a chronological timeline of capsule creation events.

        Returns:
            list[dict]: Sorted list of dicts with date and title info.
        """
        events = [
            {"date": c.created_at[:10], "title": c.title, "id": c.capsule_id}
            for c in self.capsules.values()
        ]
        return sorted(events, key=lambda e: e["date"])

    # ──────────────────────────────────────────────
    # Aggregate Counts
    # ──────────────────────────────────────────────

    def total_count(self)    -> int: return len(self.capsules)
    def locked_count(self)   -> int: return sum(1 for _ in self.get_locked())
    def unlocked_count(self) -> int: return sum(1 for _ in self.get_unlocked())
