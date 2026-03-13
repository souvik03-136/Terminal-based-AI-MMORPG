from server.game.player import Player
from server.game.inventory import Inventory
from server.ai.gemini_client import gemini
from server.ai.prompts import ITEM_USE_PROMPT
from server.ai.context_manager import PlayerContext


def _get_item_by_name(self, name: str):
    name_lower = name.lower()
    for item in self._items:
        if item.name.lower() == name_lower or name_lower in item.name.lower():
            return item
    return None


# Monkey-patch Inventory with name lookup
Inventory.get_item_by_name = _get_item_by_name


def handle_inventory(player: Player) -> str:
    return player.inventory.display()


def handle_use_item(player: Player, item_name: str, context: PlayerContext) -> str:
    item = player.inventory.get_item_by_name(item_name)
    if not item:
        return f"  Item '{item_name}' not found in your inventory."

    prompt = ITEM_USE_PROMPT.format(
        item_name=item.name,
        player_stats=str(player.stats.to_dict()),
        context=context.dungeon_summary or "standard dungeon exploration",
    )
    ai_response = gemini.generate(prompt, history=context.get_history())
    context.add_exchange(f"Uses {item.name}", ai_response)

    result = ai_response + "\n"
    if "HP_RESTORED:" in ai_response:
        try:
            amt = int(ai_response.split("HP_RESTORED:")[1].split()[0])
            healed = player.stats.heal(amt)
            result += f"  ❤  +{healed} HP restored. HP: {player.stats.hp}/{player.stats.max_hp}"
            player.inventory.remove_item(item.name)
        except (ValueError, IndexError):
            pass
    elif "WEAPON_EQUIPPED:" in ai_response:
        player.stats.attack += item.effect
        result += f"  ⚔  ATK increased by {item.effect}! New ATK: {player.stats.attack}"
        player.inventory.remove_item(item.name)

    return result