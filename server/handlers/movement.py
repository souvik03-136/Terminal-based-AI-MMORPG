import random
from server.game.player import Player
from server.game.events import EventEngine
from server.game.combat import CombatEngine
from server.ai.gemini_client import gemini
from server.ai.prompts import MOVEMENT_PROMPT
from server.ai.context_manager import PlayerContext

VALID_DIRECTIONS = {
    "n": "north", "north": "north",
    "s": "south", "south": "south",
    "e": "east",  "east": "east",
    "w": "west",  "west": "west",
}

def handle_movement(player: Player, direction: str, context: PlayerContext) -> str:
    direction_key = direction.lower().strip()
    if direction_key not in VALID_DIRECTIONS:
        return f"  '{direction}' is not a valid direction. Use: N, S, E, W"

    full_dir = VALID_DIRECTIONS[direction_key]
    dungeon_ctx = context.dungeon_summary or "A dark dungeon corridor."
    player_stats = str(player.stats.to_dict())

    prompt = MOVEMENT_PROMPT.format(
        dungeon_context=dungeon_ctx,
        player_stats=player_stats,
        direction=full_dir,
    )

    ai_response = gemini.generate(prompt, history=context.get_history())
    context.add_exchange(f"Player moves {full_dir}", ai_response)
    context.set_dungeon_summary(ai_response[:300])  # Update world context

    # Parse AI signal for events
    result_lines = [ai_response]

    if "DEAD_END" in ai_response:
        pass  # Already narrated
    elif "EVENT: AMBUSH" in ai_response or (
        EventEngine.should_trigger_event() and not "DEAD_END" in ai_response
    ):
        event_type = "AMBUSH" if "EVENT: AMBUSH" in ai_response else EventEngine.pick_event_type()
        result_lines.append(_handle_event(player, event_type))

    return "\n".join(result_lines)


def _handle_event(player: Player, event_type: str) -> str:
    if event_type == "AMBUSH":
        enemy = EventEngine.random_monster(player.stats.floor)
        player.in_combat = True
        player.current_enemy = enemy
        return (
            f"\n  ⚠  AMBUSH! A {enemy['name']} leaps from the shadows!\n"
            f"  Enemy HP: {enemy['hp']}  ATK: {enemy['attack']}  DEF: {enemy['defense']}\n"
            f"  Type /fight to attack, /flee to attempt escape, /use <item> to use an item."
        )
    elif event_type == "TRAP":
        trap = EventEngine.random_trap()
        damage = player.stats.take_damage(trap["damage"])
        return (
            f"\n  💀 TRAP! {trap['msg']}\n"
            f"  You take {damage} damage! HP: {player.stats.hp}/{player.stats.max_hp}"
        )
    elif event_type == "TREASURE":
        loot = EventEngine.random_loot(player.stats.floor)
        added = player.inventory.add_item(loot)
        if added:
            return f"\n  💰 You discover a hidden cache! Found: {loot.name} — {loot.description}"
        else:
            return f"\n  💰 Treasure ahead, but your pack is full! ({loot.name} left behind)"
    elif event_type == "PASSAGE":
        return "\n  🔍 You notice a hidden passage in the wall. Type /enter to investigate."
    return ""