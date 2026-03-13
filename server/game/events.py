import random
from typing import Dict, Any
from server.game.inventory import COMMON_LOOT, UNCOMMON_LOOT, RARE_LOOT


class EventEngine:
    """Handles random dungeon events: traps, treasure, ambushes, passages."""

    MONSTER_TEMPLATES = [
        {"name": "Goblin Scout",    "hp": 20, "attack": 6,  "defense": 2, "xp": 15, "gold": 5},
        {"name": "Skeleton",        "hp": 30, "attack": 8,  "defense": 4, "xp": 20, "gold": 8},
        {"name": "Giant Spider",    "hp": 25, "attack": 10, "defense": 3, "xp": 25, "gold": 3},
        {"name": "Dark Cultist",    "hp": 40, "attack": 12, "defense": 5, "xp": 35, "gold": 15},
        {"name": "Stone Golem",     "hp": 80, "attack": 18, "defense": 12, "xp": 75, "gold": 30},
        {"name": "Vampire Thrall",  "hp": 55, "attack": 14, "defense": 7, "xp": 50, "gold": 20},
        {"name": "Shadow Wraith",   "hp": 45, "attack": 16, "defense": 8, "xp": 60, "gold": 10},
        {"name": "Ancient Dragon",  "hp": 200, "attack": 35, "defense": 20, "xp": 300, "gold": 200},
    ]

    TRAP_TYPES = [
        {"name": "Spike Pit",     "damage": 15, "msg": "The floor gives way! Spikes impale you!"},
        {"name": "Poison Dart",   "damage": 10, "msg": "A dart flies from the wall! You feel poison spreading."},
        {"name": "Fire Trap",     "damage": 20, "msg": "Flames erupt from hidden vents!"},
        {"name": "Falling Stone", "damage": 12, "msg": "A stone slab drops from the ceiling!"},
        {"name": "Arcane Rune",   "damage": 18, "msg": "You trigger a magical rune — energy sears through you!"},
    ]

    @staticmethod
    def random_monster(floor: int = 1) -> Dict:
        """Scale monster selection to dungeon floor."""
        pool_size = min(floor + 2, len(EventEngine.MONSTER_TEMPLATES))
        template = random.choice(EventEngine.MONSTER_TEMPLATES[:pool_size]).copy()
        scale = 1 + (floor - 1) * 0.15
        template["hp"] = int(template["hp"] * scale)
        template["attack"] = int(template["attack"] * scale)
        template["xp"] = int(template["xp"] * scale)
        template["gold"] = int(template["gold"] * scale)
        return template

    @staticmethod
    def random_trap() -> Dict:
        return random.choice(EventEngine.TRAP_TYPES).copy()

    @staticmethod
    def random_loot(floor: int = 1) -> Any:
        roll = random.randint(1, 100)
        if roll <= 60:
            return random.choice(COMMON_LOOT)
        elif roll <= 85:
            return random.choice(UNCOMMON_LOOT)
        else:
            return random.choice(RARE_LOOT)

    @staticmethod
    def should_trigger_event() -> bool:
        return random.randint(1, 100) <= 25

    @staticmethod
    def pick_event_type() -> str:
        roll = random.randint(1, 100)
        if roll <= 30:
            return "AMBUSH"
        elif roll <= 55:
            return "TRAP"
        elif roll <= 80:
            return "TREASURE"
        else:
            return "PASSAGE"