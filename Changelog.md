# Changelog

All notable changes to Dungeon Explorer are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Spell system (fireball, ice bolt, heal, etc.)
- Persistent player saves (SQLite)
- Party system (group up with other players)
- Boss floor every 5th floor
- Map minimap in ASCII

---

## [1.0.0] — 2024-01-01

### Added
- Full TCP multiplayer server with per-player threading
- Google Gemini 1.5 Flash AI Dungeon Master integration
- Per-player rolling context window (20 messages) — no cross-player AI contamination
- D&D-style combat engine: d20 rolls, critical hits, glancing blows, flee mechanic
- 10-slot inventory system with item stacking, potions, weapons, armor, keys
- Random event engine: ambushes, traps, treasure, hidden passages (25% per move)
- Floor scaling: monster HP/ATK/XP scales with dungeon floor number
- Loot rarity tiers: Common (60%) / Uncommon (25%) / Rare (15%)
- Player progression: XP, leveling, stat growth (HP/ATK/DEF per level)
- Session manager with broadcast and whisper messaging
- Live leaderboard ranked by level + XP
- ASCII art welcome banner and HP bar in stats block
- Terminal color rendering in client (emoji + ANSI)
- Shorthand command aliases (n/s/e/w, f for fight, i for inv, etc.)
- Free-form AI input — any text without `/` goes to the Dungeon Master
- Docker + docker-compose support
- Taskfile with setup, dev, lint, format, test, docker tasks
- GitHub Actions: CI, Release, CodeQL, Dependency Review
- Full DOCUMENTATION.md with Mermaid architecture diagrams
- MIT License