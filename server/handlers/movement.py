from server.ai.context_manager import PlayerContext
from server.ai.gemini_client import gemini
from server.ai.prompts import MOVEMENT_PROMPT
from server.game.events import EventEngine
from server.game.player import Player

VALID_DIRECTIONS = {
    "n": "north",
    "north": "north",
    "s": "south",
    "south": "south",
    "e": "east",
    "east": "east",
    "w": "west",
    "west": "west",
}


def handle_movement(player: Player, direction: str, context: PlayerContext) -> str:
    direction_key = direction.lower().strip()
    if direction_key not in VALID_DIRECTIONS:
        return f"  '{direction}' is not a valid direction. Use: N, S, E, W"

    full_dir = VALID_DIRECTIONS[direction_key]

    # Offline mode: use the fallback engine directly for richer output
    if gemini.mode == "offline":
        from server.ai.fallback_engine import fallback

        ai_response = fallback.generate_movement(full_dir, player.stats.floor)
    else:
        dungeon_ctx = context.dungeon_summary or "A dark dungeon corridor."
        player_stats = str(player.stats.to_dict())
        prompt = MOVEMENT_PROMPT.format(
            dungeon_context=dungeon_ctx,
            player_stats=player_stats,
            direction=full_dir,
        )
        ai_response = gemini.generate(prompt, history=context.get_history())

    context.add_exchange(f"Player moves {full_dir}", ai_response)
    context.set_dungeon_summary(ai_response[:300])

    result_lines = [ai_response]

    if "DEAD_END" in ai_response:
        pass  # Already narrated, no event
    elif EventEngine.should_trigger_event():
        event_type = (
            "AMBUSH" if "EVENT: AMBUSH" in ai_response else EventEngine.pick_event_type()
        )
        result_lines.append(_handle_event(player, event_type))

    return "\n".join(result_lines)


def _handle_event(player: Player, event_type: str) -> str:
    if event_type == "AMBUSH":
        enemy = EventEngine.random_monster(player.stats.floor)
        player.in_combat = True
        player.current_enemy = enemy

        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            return fallback.generate_ambush(
                enemy["name"], enemy["hp"], enemy["attack"], enemy["defense"]
            )

        return (
            f"\n  ⚠  AMBUSH! A {enemy['name']} leaps from the shadows!\n"
            f"  Enemy HP: {enemy['hp']}  ATK: {enemy['attack']}  DEF: {enemy['defense']}\n"
            f"  Type /fight to attack, /flee to attempt escape, /use <item> to use an item."
        )

    elif event_type == "TRAP":
        trap = EventEngine.random_trap()
        damage = player.stats.take_damage(trap["damage"])

        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            narration = fallback.generate_trap(trap["name"], damage)
        else:
            narration = f"TRAP! {trap['msg']}"

        return (
            f"\n  💀 {narration}\n"
            f"  You take {damage} damage! HP: {player.stats.hp}/{player.stats.max_hp}"
        )

    elif event_type == "TREASURE":
        loot = EventEngine.random_loot(player.stats.floor)
        added = player.inventory.add_item(loot)

        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            return "\n  💰 " + fallback.generate_treasure(loot.name, full=not added)

        if added:
            return f"\n  💰 You discover a hidden cache! Found: {loot.name} — {loot.description}"
        return f"\n  💰 Treasure ahead, but your pack is full! ({loot.name} left behind)"

    elif event_type == "PASSAGE":
        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            return "\n  🔍 " + fallback.generate_passage()
        return "\n  🔍 You notice a hidden passage in the wall. Type /enter to investigate."

    return ""