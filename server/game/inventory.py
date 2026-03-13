from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class Item:
    name: str
    item_type: str          # weapon / potion / key / armor / misc
    value: int = 0          # gold value
    effect: int = 0         # damage bonus, heal amount, etc.
    description: str = ""
    quantity: int = 1

    def __str__(self):
        return f"{self.name} ({self.item_type}) — {self.description}"


class Inventory:
    MAX_SLOTS = 10

    def __init__(self):
        self._items: List[Item] = []

    def add_item(self, item: Item) -> bool:
        # Stack potions/misc
        for existing in self._items:
            if existing.name == item.name and existing.item_type == item.item_type:
                existing.quantity += item.quantity
                return True
        if len(self._items) >= self.MAX_SLOTS:
            return False
        self._items.append(item)
        return True

    def remove_item(self, name: str) -> Optional[Item]:
        for i, item in enumerate(self._items):
            if item.name.lower() == name.lower():
                if item.quantity > 1:
                    item.quantity -= 1
                    return item
                return self._items.pop(i)
        return None

    def get_item(self, index: int) -> Optional[Item]:
        if 0 <= index < len(self._items):
            return self._items[index]
        return None

    def display(self) -> str:
        if not self._items:
            return "  [Your pack is empty]"
        lines = ["\n  ╔═══ INVENTORY ══════════════════╗"]
        for i, item in enumerate(self._items):
            qty = f"x{item.quantity}" if item.quantity > 1 else "   "
            lines.append(f"  ║ [{i}] {qty} {item.name:<22} ║")
        lines.append("  ╚════════════════════════════════╝")
        return "\n".join(lines)

    def to_list(self) -> List[str]:
        return [f"{i.name} (x{i.quantity})" for i in self._items]


# Default starter kit
STARTER_ITEMS = [
    Item("Rusty Dagger",   "weapon",  value=5,  effect=3,  description="A worn blade. Better than nothing."),
    Item("Health Potion",  "potion",  value=20, effect=30, description="Restores 30 HP.", quantity=2),
    Item("Torch",          "misc",    value=2,  effect=0,  description="Lights the darkness."),
]

# Loot tables
COMMON_LOOT = [
    Item("Health Potion", "potion", value=20, effect=30, description="Restores 30 HP."),
    Item("Gold Coins",    "misc",   value=15, effect=0,  description="Shiny currency."),
    Item("Rope",          "misc",   value=5,  effect=0,  description="Useful for climbing."),
]

UNCOMMON_LOOT = [
    Item("Short Sword",     "weapon", value=40, effect=8,  description="A reliable blade."),
    Item("Leather Armor",   "armor",  value=35, effect=5,  description="+5 DEF."),
    Item("Greater Potion",  "potion", value=40, effect=60, description="Restores 60 HP."),
    Item("Skeleton Key",    "key",    value=25, effect=0,  description="Opens most locks."),
]

RARE_LOOT = [
    Item("Enchanted Blade", "weapon", value=120, effect=18, description="Glows faintly. +18 ATK."),
    Item("Ring of Vitality","misc",   value=100, effect=25, description="+25 max HP."),
    Item("Dragon Scale",    "armor",  value=150, effect=12, description="+12 DEF. Rare."),
]