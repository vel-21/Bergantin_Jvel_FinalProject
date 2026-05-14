# ✦ ChronoVault — Time-Locked Digital Capsule System

> *"Write to your future self. Seal the moment. Let time do the rest."*

ChronoVault is a CLI-based Python application that lets you create **time-locked digital capsules** — personal messages, reflections, or notes sealed until a future date you choose. Once the date arrives, your capsule unlocks and you can finally read what past-you had to say.

---

## 📋 Features

| Feature | Description |
|---|---|
| 🔒 **Time-Lock Sealing** | Capsules are unreadable until their unlock date passes |
| 🔑 **Password Protection** | Optional SHA-256 hashed password per capsule |
| 🌡️ **Mood Tracking** | Rate your mood 1–5 at creation time |
| 🏷️ **Tag System** | Organize capsules with custom tags |
| 🔍 **Full-Text Search** | Search across titles, content, and tags |
| 📊 **Mood Analytics** | ASCII bar chart of mood distribution |
| 🕰️ **Timeline View** | Chronological creation history |
| 💾 **Text Export** | Export unlocked capsules to `.txt` files |
| 📂 **Sort & Filter** | Sort by date, mood, or title; filter by tag or mood |

---

## 🐍 Python Concepts Demonstrated

- **OOP** — `Capsule` and `Vault` classes with clear attributes and methods
- **File Handling** — JSON persistence using context managers (`with open(...)`)
- **Data Structures** — Dicts, lists, sets; dispatch table for menu actions
- **Algorithms** — Custom sort (dispatch strategy), full-text search, binary search-ready structure
- **Advanced Python** — Generators (`get_unlocked`, `get_locked`), list/dict/set comprehensions, `@classmethod`, type hints

---

## 🗂️ Repository Structure

```
ChronoVault/
│
├── README.md
├── requirements.txt
│
├── src/
│   ├── main.py               # Entry point & CLI controller (ChronoVaultApp)
│   ├── models/
│   │   ├── capsule.py        # Capsule data model
│   │   └── vault.py          # Vault — manages all capsules + persistence
│   └── utils/
│       ├── display.py        # All terminal display / UI helpers
│       └── helpers.py        # Stateless utility / validation functions
│
└── data/
    ├── vault.json            # Auto-generated capsule storage
    └── exports/              # Exported .txt capsule files
```

---

## ⚙️ Installation & Setup

**Requirements:** Python 3.10 or higher (no external packages needed)

```bash
# 1. Clone the repository
git clone https://github.com/<YourUsername>/YourLastName_YourFirstName_FinalProject.git
cd YourLastName_YourFirstName_FinalProject

# 2. Run the application
python src/main.py
```

No virtual environment or pip install is needed — ChronoVault uses only Python standard library modules (`os`, `sys`, `json`, `uuid`, `hashlib`, `datetime`, `time`).

---

## 🖥️ Sample CLI Usage

```
  ╔══════════════════════════════════════════════════════╗
  ║    ░█▀▀░█░█░█▀▄░█▀█░█▀█░█▀█░█░█░█▀█░█░█░█░░░▀█▀    ║
  ║    ░▀▀▀░▀░▀░▀░▀░▀▀▀░▀░▀░▀▀▀░░▀░░▀░▀░▀▀▀░▀▀▀░░▀░    ║
  ║         ✦  Your Time-Locked Message Vault  ✦         ║
  ╚══════════════════════════════════════════════════════╝

  ℹ   Vault ready — 3 capsule(s) stored, 1 unlocked and awaiting you.

  ╔══════════════════════════════════════════════════════════╗
  ║              ✦  C H R O N O V A U L T  ✦               ║
  ╠══════════════════════════════════════════════════════════╣
  ║  [1] Seal a New Capsule       ✉️                         ║
  ║  [2] View All Capsules        📂                         ║
  ║  [3] Open a Capsule           🔓                         ║
  ...
```

### Creating a Capsule
```
  ▶ Capsule title: Letter to myself at graduation

  📝 Write your message. Type END on its own line when done.
  ──────────────────────────────────────────────────────
     > Hey future me, I wonder if you made it.
     > Did you push through? I hope so.
     > END

  ▶ Unlock date (YYYY-MM-DD): 2026-04-01
  ▶ Mood (1–5): 4
  ▶ Tags: reflection,goals,2026

  ✅  Capsule #A3F7B201 has been sealed!
  ℹ   It will unlock on April 01, 2026 (148 day(s) from now). 🕰️
```

### Opening a Capsule
```
  ▶ Enter Capsule ID: A3F7B201

  ┌──── Capsule #A3F7B201
  │  📌 Title    : Letter to myself at graduation
  │  ⏳ Status   : 🔓 UNLOCKED
  │  📅 Created  : 2025-11-05
  │  🗓  Unlocks  : 2026-04-01
  │  🙂 Mood     : ▓▓▓▓░ Good (4/5)
  │  🏷  Tags     : #2026 #goals #reflection
  │
  │  ── Message ──────────────────────────────────
  │    Hey future me, I wonder if you made it.
  │    Did you push through? I hope so.
  │  ────────────────────────────────────────────
  └─────────────────────────────────────────────────
```

---

## 🎬 Video Demonstration

📺 **YouTube Link:** `https://youtu.be/YOUR_VIDEO_ID_HERE`

---

## 👤 Author

- **Name:** Juvel S. Bergantin
- **Course:** Intermediate Programming — Final Project
- **Year/Section:** BSCS-1B
