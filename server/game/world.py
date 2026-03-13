from dataclasses import dataclass, field
from typing import Dict

@dataclass
class DungeonWorld:
    """Shared mutable world state (per-floor context, leaderboard)."""

    floor_descriptions: Dict[int, str] = field(default_factory=dict)

    def set_floor_description(self, floor: int, desc: str):
        self.floor_descriptions[floor] = desc

    def get_floor_description(self, floor: int) -> str:
        return self.floor_descriptions.get(floor, "An unexplored dungeon floor.")

# Singleton world instance shared across the server
world = DungeonWorld()