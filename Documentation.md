# Dungeon Explorer — Technical Documentation

> **Version:** 1.0.0 | **Last Updated:** 2024 | **Author:** Dungeon Explorer Team

---

## Table of Contents

1. [Project Overview](#1-project-overview)
2. [Architecture Overview](#2-architecture-overview)
3. [Component Deep Dive](#3-component-deep-dive)
4. [Data Flow Diagrams](#4-data-flow-diagrams)
5. [AI Integration](#5-ai-integration)
6. [Game Systems](#6-game-systems)
7. [Network Protocol](#7-network-protocol)
8. [Configuration Reference](#8-configuration-reference)
9. [API / Command Reference](#9-api--command-reference)
10. [Deployment Guide](#10-deployment-guide)
11. [Testing Strategy](#11-testing-strategy)
12. [Contributing](#12-contributing)

---

## 1. Project Overview

Dungeon Explorer is a **real-time multiplayer terminal RPG** built on a TCP socket server. Players connect via a CLI client, are assigned a persistent session, and explore a procedurally narrated dungeon powered by Google Gemini AI. The server maintains shared world state, per-player context windows, and routes all commands through a clean handler architecture.

### Technology Stack

| Layer | Technology |
|---|---|
| Runtime | Python 3.11+ |
| AI | Google Gemini 1.5 Flash via `google-generativeai` SDK |
| Networking | Python `socket` (TCP) + `threading` |
| Config | `python-dotenv` |
| Terminal UI | `colorama`, Unicode box-drawing characters |
| Containerisation | Docker + Docker Compose |
| Task Runner | Taskfile v3 |
| CI/CD | GitHub Actions |

---

## 2. Architecture Overview

### High-Level System Architecture

```mermaid
graph TB
    subgraph Clients["Client Layer"]
        C1[Client 1<br/>Terminal]
        C2[Client 2<br/>Terminal]
        C3[Client N<br/>Terminal]
    end

    subgraph Network["Network Layer (TCP)"]
        direction LR
        SOCK[Socket Server<br/>game_server.py<br/>:4000]
    end

    subgraph Server["Server Core"]
        direction TB
        SR[Command Router<br/>command_router.py]
        SM[Session Manager<br/>session_manager.py]
    end

    subgraph Handlers["Handler Layer"]
        HM[Movement<br/>Handler]
        HC[Combat<br/>Handler]
        HI[Inventory<br/>Handler]
        HCH[Chat<br/>Handler]
        HA[Admin<br/>Handler]
    end

    subgraph Game["Game Engine"]
        GP[Player<br/>player.py]
        GC[Combat<br/>combat.py]
        GE[Events<br/>events.py]
        GI[Inventory<br/>inventory.py]
        GD[Dice<br/>dice.py]
        GW[World<br/>world.py]
    end

    subgraph AI["AI Layer"]
        GEM[Gemini Client<br/>gemini_client.py]
        CTX[Context Manager<br/>context_manager.py]
        PRM[Prompt Templates<br/>prompts.py]
    end

    subgraph External["External Services"]
        GAPI[Google Gemini API<br/>gemini-1.5-flash]
    end

    C1 & C2 & C3 -->|TCP| SOCK
    SOCK --> SM
    SOCK --> SR
    SR --> HM & HC & HI & HCH & HA
    HM & HC & HI --> Game
    HM & HC & HI --> AI
    AI --> GEM
    GEM -->|HTTPS| GAPI
    SM -->|broadcast| SOCK
```

### Module Dependency Graph

```mermaid
graph LR
    main["server/main.py"] --> gs["game_server.py"]
    gs --> sm["session_manager.py"]
    gs --> cr["command_router.py"]
    gs --> ai_ctx["ai/context_manager.py"]
    gs --> ai_gem["ai/gemini_client.py"]
    gs --> ai_prm["ai/prompts.py"]
    gs --> gw["game/world.py"]

    cr --> hm["handlers/movement.py"]
    cr --> hc["handlers/combat_handler.py"]
    cr --> hi["handlers/inventory_handler.py"]
    cr --> hch["handlers/chat_handler.py"]
    cr --> ha["handlers/admin_handler.py"]

    hm --> ge["game/events.py"]
    hm --> ai_gem
    hm --> ai_prm
    hc --> gcbt["game/combat.py"]
    hc --> ge
    hi --> gi["game/inventory.py"]
    hi --> ai_gem

    gcbt --> gp["game/player.py"]
    gcbt --> gd["game/dice.py"]
    gp --> gi
    ge --> gd
    ge --> gi

    cfg["config.py"] --> gs
    cfg --> ai_gem
    cfg --> sm
```

---

## 3. Component Deep Dive

### 3.1 `game_server.py` — TCP Server

The entry-point for all network operations. Responsibilities:

- Binds a TCP socket to `HOST:PORT`
- Accepts incoming connections, spawning one `threading.Thread` per player
- Sends the ASCII welcome banner and prompts for player name
- Triggers the initial AI floor generation
- Runs the per-client **receive → route → respond** loop
- Handles disconnection cleanup via `_cleanup()`

```mermaid
sequenceDiagram
    participant Client
    participant GameServer
    participant SessionManager
    participant GeminiAI
    participant CommandRouter

    Client->>GameServer: TCP connect()
    GameServer->>Client: Send WELCOME_BANNER
    GameServer->>Client: "Enter your name:"
    Client->>GameServer: "Thorin"
    GameServer->>SessionManager: add_player(player)
    GameServer->>GeminiAI: generate(MAZE_GENERATION_PROMPT)
    GeminiAI-->>GameServer: Floor description
    GameServer->>Client: Welcome + floor description + stats block
    SessionManager->>All Others: "📢 Thorin has entered!"

    loop Game Loop
        Client->>GameServer: "/n"
        GameServer->>CommandRouter: route("/n", player, context)
        CommandRouter-->>GameServer: AI-narrated response
        GameServer->>Client: Response text
    end

    Client->>GameServer: disconnect
    GameServer->>SessionManager: remove_player(player)
    SessionManager->>All Others: "📢 Thorin has left."
```

### 3.2 `session_manager.py` — Session Registry

A thread-safe in-memory store mapping:
- `player_id (str)` → `Player` object
- `socket.fileno() (int)` → `player_id`

Key operations:

| Method | Description |
|---|---|
| `add_player(player)` | Register a new connection |
| `remove_player(player)` | Unregister on disconnect |
| `broadcast(msg, exclude)` | Send to all players, optionally excluding one |
| `leaderboard()` | Sorted snapshot by level + XP |

### 3.3 `command_router.py` — Command Dispatch

Routes raw string input to the appropriate handler. Applies two guards before dispatch:

1. **Death guard** — dead players can only `/respawn` or `/help`
2. **Combat guard** — players in combat can only use combat/inventory/help commands

Free-form input (no `/` prefix) is passed directly to Gemini as narrative action.

### 3.4 `ai/gemini_client.py` — Gemini Wrapper

A **singleton** wrapping `google.generativeai.GenerativeModel`. Initialised once at server startup with the `SYSTEM_PROMPT` as a system instruction.

Two modes of generation:
- **Stateless**: `generate(prompt)` — for world/floor generation
- **Stateful**: `generate(prompt, history=context.get_history())` — uses per-player rolling context

### 3.5 `ai/context_manager.py` — Per-Player Memory

Each player gets their own `PlayerContext` instance holding:
- A `deque(maxlen=20)` of `{role, parts}` dicts (the Gemini conversation format)
- A `dungeon_summary` string — the last 300 chars of AI output used as world context in future prompts

This prevents cross-player AI contamination and manages token budget via the rolling window.

### 3.6 `game/player.py` — Player State

```mermaid
classDiagram
    class Player {
        +str name
        +str player_id
        +tuple address
        +socket socket
        +PlayerStats stats
        +Inventory inventory
        +bool in_combat
        +dict current_enemy
        +bool is_alive
        +send(message)
        +stats_block() str
    }

    class PlayerStats {
        +int hp
        +int max_hp
        +int attack
        +int defense
        +int level
        +int xp
        +int xp_to_next
        +int gold
        +int floor
        +is_alive() bool
        +take_damage(amount) int
        +heal(amount) int
        +gain_xp(amount) bool
        -_level_up()
        +to_dict() dict
    }

    class Inventory {
        +int MAX_SLOTS = 10
        +add_item(item) bool
        +remove_item(name) Item
        +get_item(index) Item
        +get_item_by_name(name) Item
        +display() str
        +to_list() list
    }

    class Item {
        +str name
        +str item_type
        +int value
        +int effect
        +str description
        +int quantity
    }

    Player --> PlayerStats
    Player --> Inventory
    Inventory --> Item
```

---

## 4. Data Flow Diagrams

### 4.1 Movement Command Flow

```mermaid
flowchart TD
    A[Player types '/n'] --> B{Valid direction?}
    B -- No --> Z1[Return error]
    B -- Yes --> C[Build MOVEMENT_PROMPT\nwith dungeon context + player stats]
    C --> D[Call Gemini API\nwith player history]
    D --> E[Receive AI narration]
    E --> F[Update PlayerContext\ndungeon_summary]
    F --> G{Random event\ntrigger? 25%}
    G -- No --> H[Return narration]
    G -- Yes --> I[Pick event type\nAMBUSH/TRAP/TREASURE/PASSAGE]
    I --> J{Event type}
    J -- AMBUSH --> K[Spawn monster\nset player.in_combat = True]
    J -- TRAP --> L[Deal damage\nto player]
    J -- TREASURE --> M[Add item\nto inventory]
    J -- PASSAGE --> N[Hint message]
    K & L & M & N --> O[Append event text to narration]
    O --> H
```

### 4.2 Combat Round Flow

```mermaid
flowchart TD
    A[Player types '/fight'] --> B{player.in_combat?}
    B -- No --> Z1[Return: not in combat]
    B -- Yes --> C[Roll d20 for player attack]
    C --> D{Roll result}
    D -- 20 = CRIT --> E[damage = attack × 2]
    D -- ≥8 = HIT --> F[damage = attack + d6]
    D -- <8 = MISS --> G[damage = attack ÷ 2]
    E & F & G --> H[Apply enemy defense\nactual = max 1, dmg - def÷2]
    H --> I[Subtract from enemy HP]
    I --> J[Enemy attacks player\nroll d20]
    J --> K[Apply player defense\nsubtract from player HP]
    K --> L{Enemy HP ≤ 0?}
    L -- Yes --> M[Award XP + Gold\nDrop loot item\nClear combat state]
    L -- No --> N{Player HP ≤ 0?}
    N -- Yes --> O[Set player.is_alive = False\nBroadcast death\nPrompt /respawn]
    N -- No --> P[Return combat summary\nHP bars for both sides]
    M --> P
```

### 4.3 AI Prompt Lifecycle

```mermaid
sequenceDiagram
    participant Handler
    participant ContextManager
    participant GeminiClient
    participant GeminiAPI

    Handler->>ContextManager: get_history()
    ContextManager-->>Handler: list of {role, parts} dicts

    Handler->>Handler: Format prompt template\n(inject dungeon_summary, player_stats)

    Handler->>GeminiClient: generate(prompt, history)
    GeminiClient->>GeminiAPI: POST /v1/generateContent\n{model, system_instruction, history + prompt}
    GeminiAPI-->>GeminiClient: response.text

    GeminiClient-->>Handler: AI narration string

    Handler->>ContextManager: add_exchange(user_msg, ai_response)
    Note over ContextManager: deque(maxlen=20) auto-drops oldest

    Handler->>ContextManager: set_dungeon_summary(response[:300])
    Handler-->>Player: Final response string
```

---

## 5. AI Integration

### 5.1 Model Configuration

```
Model:              gemini-1.5-flash
System instruction: SYSTEM_PROMPT (DM persona + world rules)
Context window:     Rolling 20 messages per player
Temperature:        Default (0.9) — creative but coherent
Max output tokens:  Default (Gemini manages)
```

### 5.2 Prompt Templates

| Prompt | Trigger | Key Variables |
|---|---|---|
| `SYSTEM_PROMPT` | Model init (once) | — (static DM persona) |
| `MAZE_GENERATION_PROMPT` | `/new_floor`, first login | — |
| `MOVEMENT_PROMPT` | `/n /s /e /w` | `dungeon_context`, `player_stats`, `direction` |
| `COMBAT_PROMPT` | (future enhancement) | `player_stats`, `enemy` |
| `ITEM_USE_PROMPT` | `/use <item>` | `item_name`, `player_stats`, `context` |

### 5.3 AI Signal Parsing

AI responses embed signal tokens that handlers parse to trigger game mechanics:

| Token | Handler | Effect |
|---|---|---|
| `DEAD_END` | movement.py | No event triggered, narration only |
| `EVENT: AMBUSH` | movement.py | Force spawns a monster |
| `EVENT: TRAP` | movement.py | Force triggers trap damage |
| `HP_RESTORED: <n>` | inventory_handler.py | Heals player by n HP |
| `WEAPON_EQUIPPED: <name>` | inventory_handler.py | Adds item.effect to player.attack |
| `PLAYER_DIED` | (future) | Narrate death (currently handled by HP check) |
| `ENEMY_DEFEATED` | (future) | Narrate victory (currently handled by HP check) |

### 5.4 Context Isolation

Each player maintains a completely independent `PlayerContext`. There is **no shared AI history** between players. This means:

- Player A's dungeon narrative does not affect Player B's AI responses
- Token costs scale linearly with player count (not quadratically)
- Players can be on different floors with entirely different world states

---

## 6. Game Systems

### 6.1 Combat System

Combat uses a simplified **d20 system**:

```
Attack roll = d20()
  20        → Critical hit  (damage × 2)
  8–19      → Hit           (damage + d6)
  1–7       → Glancing blow (damage ÷ 2)

Actual damage = max(1, raw_damage − (defender_defense ÷ 2))
```

Flee mechanic: 40% success rate. On failure, the enemy gets a free attack.

### 6.2 Event System

```mermaid
pie title Random Event Distribution (25% trigger chance per move)
    "Ambush (monster)" : 30
    "Trap (damage)" : 25
    "Treasure (loot)" : 25
    "Hidden Passage" : 20
```

### 6.3 Loot System

```mermaid
pie title Loot Rarity Distribution
    "Common" : 60
    "Uncommon" : 25
    "Rare" : 15
```

Monster difficulty scales with `floor` number:
```
hp     = base_hp     × (1 + (floor − 1) × 0.15)
attack = base_attack × (1 + (floor − 1) × 0.15)
xp     = base_xp     × (1 + (floor − 1) × 0.15)
```

### 6.4 Leveling Curve

| Level | XP Required | HP | Attack | Defense |
|---|---|---|---|---|
| 1 | 0 | 100 | 10 | 5 |
| 2 | 100 | 115 | 13 | 7 |
| 3 | 150 | 130 | 16 | 9 |
| 4 | 225 | 145 | 19 | 11 |
| 5 | 337 | 160 | 22 | 13 |
| N | prev × 1.5 | +15 per level | +3 per level | +2 per level |

---

## 7. Network Protocol

Dungeon Explorer uses a simple **raw TCP text protocol**. There is no binary framing — messages are UTF-8 strings delimited by newlines.

```
Client → Server:  /fight\n
Server → Client:  ⚔  You strike Goblin for 12 dmg!\n
                  🗡  Goblin hits you for 4 dmg!\n
                  Enemy — HP: 8   |   You — HP: 91/100 (alive)\n
```

**Buffer size:** 4096 bytes per read. Long AI responses may be chunked by the OS; the client's receive loop handles this transparently.

**Encoding:** UTF-8 with `errors='replace'` on decode — handles malformed bytes gracefully.

### Connection Lifecycle

```mermaid
stateDiagram-v2
    [*] --> Connected: TCP accept()
    Connected --> Naming: Send banner
    Naming --> Active: Receive player name
    Active --> InCombat: Encounter triggered
    InCombat --> Active: Combat resolved
    Active --> Dead: HP reaches 0
    Dead --> Active: /respawn
    Active --> Disconnected: Client closes / error
    InCombat --> Disconnected: Client closes / error
    Disconnected --> [*]: _cleanup()
```

---

## 8. Configuration Reference

All values loaded from `.env` via `python-dotenv`.

| Variable | Type | Default | Required | Description |
|---|---|---|---|---|
| `GEMINI_API_KEY` | string | — | ✅ Yes | Google Gemini API key |
| `PORT` | int | `4000` | No | TCP port to bind |
| `HOST` | string | `localhost` | No | Bind address (`0.0.0.0` for Docker/LAN) |
| `MAX_PLAYERS` | int | `10` | No | Max concurrent player connections |
| `LOG_LEVEL` | string | `INFO` | No | `DEBUG / INFO / WARNING / ERROR` |

Compiled `Config` class constants (not overridable via `.env`):

| Constant | Value | Description |
|---|---|---|
| `BUFFER_SIZE` | `4096` | TCP receive buffer in bytes |
| `AI_MODEL` | `gemini-1.5-flash` | Gemini model identifier |
| `MAX_CONTEXT_MESSAGES` | `20` | Rolling AI history window per player |

---

## 9. API / Command Reference

### Full Command Table

| Command | Args | Guard | AI Call | Description |
|---|---|---|---|---|
| `/n /s /e /w` | — | alive, not combat | ✅ Yes | Move in direction |
| `/look` | — | alive | No | Show dungeon summary |
| `/fight` | — | in_combat | No | Attack current enemy |
| `/flee` | — | in_combat | No | Escape combat (40%) |
| `/respawn` | — | dead | No | Restart after death |
| `/inv` | — | alive | No | Show inventory |
| `/use` | `<item name>` | alive | ✅ Yes | Use/equip item |
| `/msg` | `<text>` | alive | No | Broadcast chat |
| `/w` | `<name> <text>` | alive | No | Whisper to player |
| `/who` | — | alive | No | List online players |
| `/stats` | — | alive | No | Show stat block |
| `/roll` | `[sides]` | alive | No | Roll dice (d2–d100) |
| `/new_floor` | — | alive | ✅ Yes | Descend to next floor |
| `/leaderboard` | — | alive | No | Top 10 rankings |
| `/help` | — | always | No | Show help menu |
| `<free text>` | — | alive, not combat | ✅ Yes | Free-form AI action |

### Combat Guards

Commands blocked during combat (must fight or flee first):
`/n`, `/s`, `/e`, `/w`, `/look`, `/msg`, `/w`, `/who`, `/stats`, `/roll`, `/new_floor`, `/leaderboard`

---

## 10. Deployment Guide

### Local Development

```bash
task setup      # First time
task server     # Start server
task client     # Connect client
```

### Production (Linux VPS)

```bash
# 1. Clone and install
git clone https://github.com/yourusername/dungeon-explorer.git
cd dungeon-explorer
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env
nano .env   # Set GEMINI_API_KEY, HOST=0.0.0.0

# 3. Run as a systemd service
sudo nano /etc/systemd/system/dungeon-explorer.service
```

```ini
# /etc/systemd/system/dungeon-explorer.service
[Unit]
Description=Dungeon Explorer MMORPG Server
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/dungeon-explorer
EnvironmentFile=/home/ubuntu/dungeon-explorer/.env
ExecStart=/home/ubuntu/dungeon-explorer/.venv/bin/python -m server.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable dungeon-explorer
sudo systemctl start dungeon-explorer
sudo systemctl status dungeon-explorer
```

### Docker Compose (Recommended for VPS)

```bash
cp .env.example .env     # Add GEMINI_API_KEY, set HOST=0.0.0.0
docker-compose up -d     # Detached
docker-compose logs -f   # Follow logs
```

### Firewall (UFW)

```bash
sudo ufw allow 4000/tcp
sudo ufw reload
```

Players connect with:
```bash
python -m client.main --host YOUR_SERVER_IP --port 4000
```

---

## 11. Testing Strategy

### Test Layout

```
tests/
├── unit/
│   ├── test_dice.py
│   ├── test_combat.py
│   ├── test_inventory.py
│   ├── test_player.py
│   ├── test_events.py
│   └── test_command_router.py
├── integration/
│   ├── test_session_manager.py
│   └── test_game_server.py
└── conftest.py
```

### Key Test Areas

| Module | What to Test |
|---|---|
| `dice.py` | Roll distribution, crit/miss boundary conditions |
| `combat.py` | Damage calculation, death detection, loot grant |
| `inventory.py` | Stack logic, slot limits, name lookup |
| `player.py` | XP/level-up curve, HP clamping, damage reduction |
| `events.py` | Monster scaling formula, loot rarity distribution |
| `command_router.py` | Guard conditions, unknown command fallback |
| `session_manager.py` | Concurrent add/remove, broadcast exclusion |

### Running Tests

```bash
task test           # All tests
task test:cov       # With coverage (target: >80%)
```

---

## 12. Contributing

### Development Workflow

```mermaid
gitGraph
   commit id: "main"
   branch feature/new-spell-system
   checkout feature/new-spell-system
   commit id: "Add spell dataclass"
   commit id: "Add spell handler"
   commit id: "Add tests"
   checkout main
   merge feature/new-spell-system id: "PR merged"
   branch hotfix/combat-crash
   checkout hotfix/combat-crash
   commit id: "Fix divide by zero"
   checkout main
   merge hotfix/combat-crash id: "Hotfix merged"
```

### Pull Request Checklist

- [ ] All tests pass (`task test`)
- [ ] Code passes lint + format (`task check`)
- [ ] New features include tests
- [ ] `DOCUMENTATION.md` updated if architecture changed
- [ ] `.env.example` updated if new config added

### Extending the Game

**Adding a new command:**
1. Add handler function in `server/handlers/<relevant>.py`
2. Register the command in `server/command_router.py` `_dispatch()`
3. Add help text in `server/handlers/admin_handler.py` `handle_help()`
4. Add tests in `tests/unit/test_command_router.py`

**Adding a new item type:**
1. Add the `Item` to loot tables in `server/game/inventory.py`
2. Add parsing logic in `server/handlers/inventory_handler.py` `handle_use_item()`
3. Add a prompt template in `server/ai/prompts.py` if AI narration is needed

**Adding a new monster:**
1. Append to `MONSTER_TEMPLATES` in `server/game/events.py`
2. Adjust pool_size logic in `EventEngine.random_monster()` if floor-gated

---

