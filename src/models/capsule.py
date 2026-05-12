"""
capsule.py — ChronoVault
========================
Defines the Capsule data model, representing a single time-locked
digital message. Each capsule holds content, an unlock date, mood
metadata, tags, and an optional password hash.
"""

import hashlib
from datetime import datetime


class Capsule:
    """
    A time-locked digital capsule containing a message sealed until
    a future date.

    Attributes:
        capsule_id (str): Unique 8-character identifier.
        title (str): Short title of the capsule.
        content (str): The sealed message/content.
        created_at (str): ISO-format creation timestamp.
        unlock_date (str): ISO-format date when the capsule becomes readable.
        mood (int): Mood rating at creation time (1–5).
        tags (set): A set of string tags for categorization.
        password_hash (str | None): SHA-256 hash of optional password.
        is_opened (bool): Whether the capsule has been read at least once.
    """

    MOOD_MAP = {
        1: ("Terrible", "▓░░░░", "😞"),
        2: ("Bad",      "▓▓░░░", "😕"),
        3: ("Neutral",  "▓▓▓░░", "😐"),
        4: ("Good",     "▓▓▓▓░", "🙂"),
        5: ("Amazing",  "▓▓▓▓▓", "😄"),
    }

    def __init__(
        self,
        capsule_id: str,
        title: str,
        content: str,
        unlock_date: str,
        mood: int = 3,
        tags: list = None,
        password_hash: str = None,
    ):
        """
        Initialize a new Capsule instance.

        Args:
            capsule_id (str): Unique identifier.
            title (str): Capsule title.
            content (str): Sealed message content.
            unlock_date (str): ISO-format unlock date string.
            mood (int): Mood score from 1 (worst) to 5 (best).
            tags (list, optional): List of tag strings.
            password_hash (str, optional): Hashed password for protection.
        """
        self.capsule_id = capsule_id
        self.title = title
        self.content = content
        self.created_at = datetime.now().isoformat()
        self.unlock_date = unlock_date
        self.mood = mood
        self.tags = set(tags) if tags else set()
        self.password_hash = password_hash
        self.is_opened = False

    # ──────────────────────────────────────────────
    # Core Methods
    # ──────────────────────────────────────────────

    def is_unlocked(self) -> bool:
        """
        Determine whether the capsule's unlock date has passed.

        Returns:
            bool: True if the current datetime is past the unlock date.
        """
        return datetime.now() >= datetime.fromisoformat(self.unlock_date)

    def verify_password(self, password: str) -> bool:
        """
        Verify a plaintext password against the stored SHA-256 hash.

        Args:
            password (str): The password to verify.

        Returns:
            bool: True if correct or no password is set.
        """
        if self.password_hash is None:
            return True
        hashed = hashlib.sha256(password.encode()).hexdigest()
        return hashed == self.password_hash

    def get_mood_display(self) -> tuple:
        """
        Retrieve the visual mood label, bar, and emoji for this capsule.

        Returns:
            tuple: (label, bar, emoji) strings for display.
        """
        return self.MOOD_MAP.get(self.mood, ("Unknown", "?????", "❓"))

    def days_remaining(self) -> int:
        """
        Compute how many days remain until the capsule unlocks.

        Returns:
            int: Days remaining; 0 if already unlocked.
        """
        unlock = datetime.fromisoformat(self.unlock_date)
        delta = unlock - datetime.now()
        return max(0, delta.days)

    # ──────────────────────────────────────────────
    # Serialization
    # ──────────────────────────────────────────────

    def to_dict(self) -> dict:
        """
        Serialize the capsule to a JSON-compatible dictionary.

        Returns:
            dict: Dictionary representation of the capsule.
        """
        return {
            "capsule_id":    self.capsule_id,
            "title":         self.title,
            "content":       self.content,
            "created_at":    self.created_at,
            "unlock_date":   self.unlock_date,
            "mood":          self.mood,
            "tags":          list(self.tags),
            "password_hash": self.password_hash,
            "is_opened":     self.is_opened,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Capsule":
        """
        Deserialize a Capsule from a dictionary (e.g., loaded from JSON).

        Args:
            data (dict): Dictionary with capsule fields.

        Returns:
            Capsule: A reconstructed Capsule instance.
        """
        capsule = cls(
            capsule_id    = data["capsule_id"],
            title         = data["title"],
            content       = data["content"],
            unlock_date   = data["unlock_date"],
            mood          = data.get("mood", 3),
            tags          = data.get("tags", []),
            password_hash = data.get("password_hash"),
        )
        capsule.created_at = data["created_at"]
        capsule.is_opened  = data.get("is_opened", False)
        return capsule

    def __repr__(self) -> str:
        return f"<Capsule id={self.capsule_id} title='{self.title}' unlocked={self.is_unlocked()}>"
