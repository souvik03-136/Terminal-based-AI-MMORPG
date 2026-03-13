import uuid
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from server.game.inventory import Inventory, Item, STARTER_ITEMS

@dataclass
class PlayerStats:
    max_hp: int = 100
    hp: int = 100
    attack: int = 10
    defense: int = 5
    level: int = 1
    xp: int = 0
    xp_to_next: int = 100
    gold: int = 0
    floor: int = 1

    def is_alive(self) -> bool:
        return self.hp > 0

    def take_damage(self, amount: int) -> int:
        actual = max(1, amount - self.defense // 2)
        self.hp = max(0, self.hp - actual)
        return actual

    def heal(self, amount: int) -> int:
        before = self.hp
        self.hp = min(self.max_hp, self.hp + amount)
        return self.hp - before

    def gain_xp(self, amount: int) -> bool:
        """Returns True if leveled up."""
        self.xp += amount
        if self.xp >= self.xp_to_next:
            self._level_up()
            return True
        return False

    def _level_up(self):
        self.level += 1
        self.xp -= self.xp_to_next
        self.xp_to_next = int(self.xp_to_next * 1.5)
        self.max_hp += 15
        self.hp = self.max_hp
        self.attack += 3
        self.defense += 2

    def to_dict(self) -> dict:
        return {
            "HP": f"{self.hp}/{self.max_hp}",
            "ATK": self.attack,
            "DEF": self.defense,
            "LVL": self.level,
            "XP": f"{self.xp}/{self.xp_to_next}",
            "Gold": self.gold,
            "Floor": self.floor,
        }


@dataclass
class Player:
    name: str
    address: tuple
    socket: object  # socket.socket — not type-hinted to avoid circular import
    player_id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    stats: PlayerStats = field(default_factory=PlayerStats)
    inventory: Inventory = field(default_factory=Inventory)
    in_combat: bool = False
    current_enemy: Optional[Dict] = None
    is_alive: bool = True

    def __post_init__(self):
        for item in STARTER_ITEMS:
            self.inventory.add_item(item)

    def send(self, message: str):
        try:
            self.socket.send((message + "\n").encode())
        except Exception:
            pass  # Handled at connection level

    def stats_block(self) -> str:
        s = self.stats
        bar_filled = int((s.hp / s.max_hp) * 20)
        hp_bar = "█" * bar_filled + "░" * (20 - bar_filled)
        return (
            f"\n╔══════════════════════════════╗\n"
            f"║  {self.name:<10}  LVL {s.level:<3}  Floor {s.floor}  ║\n"
            f"║  HP [{hp_bar}] {s.hp}/{s.max_hp}\n"
            f"║  ATK:{s.attack}  DEF:{s.defense}  XP:{s.xp}/{s.xp_to_next}  Gold:{s.gold}g\n"
            f"╚══════════════════════════════╝"
        )