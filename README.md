# ⚔ Dungeon Explorer — Terminal-Based AI MMORPG

A production-grade, real-time multiplayer text adventure powered by **Google Gemini AI**. Multiple players connect over raw TCP, explore a procedurally narrated dungeon, fight monsters, loot treasure, level up, and chat — all from the terminal.

---

## Features

- **AI Dungeon Master** — Gemini 1.5 Flash narrates every move, combat, and event uniquely
- **Real-time Multiplayer** — TCP sockets + threading, up to 10 concurrent players
- **Full D&D Combat Engine** — d20 rolls, critical hits, advantage/disadvantage, flee mechanics
- **Inventory System** — 10-slot pack, stackable items, potions/weapons/armor/keys
- **Random Dungeon Events** — Ambushes, traps, hidden treasure, secret passages
- **Player Progression** — XP, leveling, gold, multi-floor dungeon (floor scaling)
- **Per-Player AI Context** — Rolling 20-message conversation window per player, no bleed
- **In-Game Social** — Broadcast chat, private whispers, join/leave announcements
- **Live Leaderboard** — Ranked by level + XP
- **Docker Support** — Single-command deployment

---

## Quick Start

### 1. Clone & Install

```bash
git clone https://github.com/souvik03-136/Terminal-based-AI-MMORPG.git
cd Terminal-based-AI-MMORPG
pip install -r requirements.txt
```

### 2. Configure

```bash
cp .env.example .env
# Open .env and fill in your GEMINI_API_KEY
```

### 3. Run the Server

```bash
python -m server.main
```

### 4. Connect Players (open a new terminal per player)

```bash
python -m client.main

# Custom host/port:
python -m client.main --host localhost --port 4000
```

---

## Docker

```bash
docker-compose up --build
```

Then connect clients normally:

```bash
python -m client.main
```

---

## Command Reference

### Movement

| Command | Description |
|---|---|
| `/n` or `/north` | Move north |
| `/s` or `/south` | Move south |
| `/e` or `/east` | Move east |
| `/w` or `/west` | Move west |
| `/look` | Re-describe your current location |

### Combat

| Command | Description |
|---|---|
| `/fight` or `f` | Attack the current enemy |
| `/flee` | Attempt to escape (40% chance) |
| `/respawn` | Restart after death (−20 gold penalty) |

### Inventory

| Command | Description |
|---|---|
| `/inv` or `i` | Open your inventory |
| `/use <item name>` | Use an item by name |

### Character

| Command | Description |
|---|---|
| `/stats` | Display your full stat block + HP bar |
| `/roll [sides]` | Roll a dice (default: d20, max: d100) |
| `/new_floor` | Descend to the next dungeon floor |

### Social

| Command | Description |
|---|---|
| `/msg <text>` | Broadcast a message to all players |
| `/w <name> <msg>` | Whisper privately to a player |
| `/who` | List all online adventurers |
| `/leaderboard` | Show rankings |

### Other

| Command | Description |
|---|---|
| `/help` | Show in-game help menu |
| `/quit` or `q` | Disconnect |

> **Tip:** Any text *without* a `/` is sent directly to the AI Dungeon Master as a free-form action or question.

---

## Shorthand Aliases (client-side)

The client expands these before sending:

| Type | Alias | Expands To |
|---|---|---|
| Movement | `n`, `s`, `e`, `w` | `/n`, `/s`, `/e`, `/w` |
| Combat | `f`, `fight` | `/fight` |
| Inventory | `i`, `inv` | `/inv` |
| Help | `h`, `help` | `/help` |
| Stats | `stats` | `/stats` |
| Quit | `q`, `quit`, `exit` | `/quit` |

---

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | *(required)* | Your Google Gemini API key |
| `PORT` | `4000` | Server listen port |
| `HOST` | `localhost` | Server bind address |
| `MAX_PLAYERS` | `10` | Maximum concurrent connections |
| `LOG_LEVEL` | `INFO` | Logging verbosity (DEBUG/INFO/WARNING) |

---

## Project Structure

```
Terminal-based-AI-MMORPG/
├── server/
│   ├── main.py               Entry point
│   ├── config.py             Environment config
│   ├── game_server.py        TCP server, onboarding, game loop
│   ├── session_manager.py    Live session tracking, broadcast
│   ├── command_router.py     Routes commands to handlers
│   ├── ai/
│   │   ├── gemini_client.py  Gemini API singleton wrapper
│   │   ├── prompts.py        All AI prompt templates
│   │   └── context_manager.py  Per-player conversation history
│   ├── game/
│   │   ├── player.py         Player dataclass + stat block
│   │   ├── combat.py         D&D combat engine
│   │   ├── inventory.py      Item system + loot tables
│   │   ├── dice.py           Dice roller (d20, d6, advantage)
│   │   ├── events.py         Random event engine
│   │   └── world.py          Shared dungeon world state
│   └── handlers/
│       ├── movement.py       Movement + event triggering
│       ├── combat_handler.py Fight/flee/respawn logic
│       ├── inventory_handler.py  Item use + effects
│       ├── chat_handler.py   Broadcast + whisper
│       └── admin_handler.py  Help, who, roll, leaderboard
└── client/
    ├── main.py               Client entry point
    ├── connection.py         TCP socket wrapper
    ├── display.py            Terminal color rendering
    └── input_handler.py      Input parsing + aliases
```

---

## Game Mechanics

### Combat Flow

1. Player enters a room → 25% chance of ambush, or triggers one via exploration
2. Enemy spawns, scaled to current floor
3. Each `/fight` = one full round: player attacks, then enemy counterattacks
4. d20 roll determines hit quality: natural 20 = critical (2× damage)
5. On enemy death: XP + gold + random loot drop
6. On player death: broadcast announcement, `/respawn` to restart at floor 1

### Event System

Each movement has a 25% chance to trigger a random event:

| Event | Probability | Effect |
|---|---|---|
| Ambush | 30% of events | Spawns an enemy scaled to floor |
| Trap | 25% of events | Instant damage (spike pit, poison dart, etc.) |
| Treasure | 25% of events | Random loot added to inventory |
| Hidden Passage | 20% of events | Narrative discovery, optional `/enter` |

### Leveling

- Each floor's enemies yield more XP (15% scaling per floor)
- On level up: +15 max HP (full heal), +3 ATK, +2 DEF
- XP threshold increases by 1.5× each level

### Loot Rarity

| Rarity | Roll Range | Examples |
|---|---|---|
| Common | 1–60 | Health Potion, Gold Coins, Rope |
| Uncommon | 61–85 | Short Sword, Leather Armor, Skeleton Key |
| Rare | 86–100 | Enchanted Blade, Ring of Vitality, Dragon Scale |

---

## Requirements

```
google-generativeai>=0.8.0
python-dotenv>=1.0.0
colorama>=0.4.6
pyfiglet>=1.0.2
```

Python 3.9+ recommended.

---

## License

MIT — use freely, contribute openly.