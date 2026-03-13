import random
from typing import Dict

from server.ai.context_manager import PlayerContext
from server.ai.gemini_client import gemini
from server.game.combat import CombatEngine
from server.game.events import EventEngine
from server.game.player import Player
from server.session_manager import sessions


def handle_fight(player: Player, context: PlayerContext) -> str:
    if not player.in_combat or not player.current_enemy:
        return "  You are not in combat. Explore the dungeon first."

    enemy: Dict = player.current_enemy
    p_dmg, p_crit = CombatEngine.player_attacks(player)
    e_dmg, e_crit = CombatEngine.enemy_attacks(player)

    # Narration: offline uses fallback, online uses CombatEngine summary
    if gemini.mode == "offline":
        from server.ai.fallback_engine import fallback

        narration = fallback.generate_combat_round(
            player.name,
            enemy["name"],
            p_dmg,
            e_dmg,
            p_crit,
            e_crit,
            enemy["hp"],
            player.stats.hp,
            player.stats.max_hp,
        )
    else:
        narration = CombatEngine.combat_summary(player, p_dmg, e_dmg, p_crit, e_crit)

    outcome_msg = ""

    if enemy["hp"] <= 0:
        xp_gain = int(enemy["xp"])
        gold_gain = int(enemy["gold"])
        player.stats.gain_xp(xp_gain)
        player.stats.gold += gold_gain
        player.in_combat = False

        loot = EventEngine.random_loot(player.stats.floor)
        player.inventory.add_item(loot)

        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            victory_line = fallback.generate_victory(enemy["name"])
        else:
            victory_line = f"{enemy['name']} has been slain!"

        outcome_msg = (
            f"\n  🏆 {victory_line}\n"
            f"  +{xp_gain} XP  +{gold_gain} Gold  Loot: {loot.name}\n"
            f"{player.stats_block()}"
        )
        player.current_enemy = None

    elif not player.stats.is_alive():
        player.is_alive = False
        player.in_combat = False

        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            death_line = fallback.generate_death(enemy["name"])
        else:
            death_line = "You have fallen in the darkness..."

        outcome_msg = (
            f"\n  💀 ════════════════════════════════ 💀\n"
            f"  {death_line}\n"
            f"       {player.name} has met their end.\n"
            f"  💀 ════════════════════════════════ 💀\n"
            f"  Type /respawn to begin again."
        )
        sessions.broadcast(
            f"  ☠  {player.name} was slain by a {enemy['name']}...",
            exclude=player,
        )

    return narration + outcome_msg


def handle_flee(player: Player, context: PlayerContext) -> str:
    if not player.in_combat or not player.current_enemy:
        return "  You're not in combat."
    enemy: Dict = player.current_enemy
    if random.randint(1, 100) <= 40:
        player.in_combat = False
        player.current_enemy = None
        return (
            "  🏃 You manage to break away and flee into a dark corridor!\n"
            "  Your heart pounds... but you're safe. For now."
        )
    else:
        e_dmg, _ = CombatEngine.enemy_attacks(player)
        return (
            f"  You try to flee, but {enemy['name']} cuts you off!\n"
            f"  You take {e_dmg} damage in the attempt!"
            f" HP: {player.stats.hp}/{player.stats.max_hp}"
        )


def handle_respawn(player: Player) -> str:
    player.stats.hp = player.stats.max_hp
    player.stats.xp = 0
    player.stats.floor = 1
    player.stats.gold = max(0, player.stats.gold - 20)
    player.is_alive = True
    player.in_combat = False
    player.current_enemy = None
    return (
        f"\n  ✨ You awaken at the dungeon entrance, gasping...\n"
        f"  The darkness gave you back. This time.\n"
        f"  (Lost 20 gold penalty. Floor reset to 1)\n"
        f"{player.stats_block()}"
    )