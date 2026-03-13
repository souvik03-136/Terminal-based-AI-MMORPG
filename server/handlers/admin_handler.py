from server.game.player import Player
from server.session_manager import sessions


def handle_help(player: Player) -> str:
    return """
  ╔══════════════════════════════════════════╗
  ║           DUNGEON EXPLORER — HELP        ║
  ╠══════════════════════════════════════════╣
  ║  MOVEMENT                                ║
  ║   /n /s /e /w  — Move in a direction     ║
  ║   /look        — Re-describe current area║
  ║                                          ║
  ║  COMBAT                                  ║
  ║   /fight       — Attack current enemy    ║
  ║   /flee        — Try to escape combat    ║
  ║   /respawn     — Restart after death     ║
  ║                                          ║
  ║  INVENTORY                               ║
  ║   /inv         — Show inventory          ║
  ║   /use <item>  — Use an item by name     ║
  ║                                          ║
  ║  SOCIAL                                  ║
  ║   /msg <text>  — Broadcast to all        ║
  ║   /w <name> <msg> — Whisper a player     ║
  ║   /who         — List online players     ║
  ║   /leaderboard — Show rankings           ║
  ║                                          ║
  ║  GAME                                    ║
  ║   /stats       — Show your stats         ║
  ║   /roll [sides] — Roll a dice            ║
  ║   /new_floor   — Descend deeper          ║
  ║   /help        — Show this menu          ║
  ╚══════════════════════════════════════════╝"""


def handle_who(player: Player) -> str:
    players = sessions.all_players()
    if not players:
        return "  No one is here."
    lines = [f"\n  ⚔  {len(players)} Adventurer(s) Online:"]
    for p in players:
        marker = " ← you" if p.player_id == player.player_id else ""
        lines.append(f"    • {p.name} (LVL {p.stats.level}, Floor {p.stats.floor}){marker}")
    return "\n".join(lines)


def handle_roll(player: Player, args: str) -> str:
    from server.game.dice import Dice
    sides = 20
    if args.strip().isdigit():
        sides = min(max(int(args.strip()), 2), 100)
    result, rolls = Dice.roll(sides)
    return f"  🎲 Rolling d{sides}... [{', '.join(map(str, rolls))}] = {result}"


def handle_new_floor(player: Player, context) -> str:
    from server.ai.gemini_client import gemini
    from server.ai.prompts import MAZE_GENERATION_PROMPT
    from server.game.world import world
    player.stats.floor += 1
    ai_response = gemini.generate(MAZE_GENERATION_PROMPT)
    world.set_floor_description(player.stats.floor, ai_response)
    context.set_dungeon_summary(ai_response[:300])
    context.add_exchange("Descends to new floor", ai_response)
    sessions.broadcast(
        f"\n  📢 {player.name} has descended to Floor {player.stats.floor}!",
        exclude=player
    )
    return f"\n  🔻 You descend deeper into the dungeon...\n\n{ai_response}\n{player.stats_block()}"