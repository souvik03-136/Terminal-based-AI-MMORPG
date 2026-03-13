from server.game.player import Player
from server.game.combat import CombatEngine
from server.game.events import EventEngine
from server.ai.gemini_client import gemini
from server.ai.prompts import COMBAT_PROMPT
from server.ai.context_manager import PlayerContext
from server.session_manager import sessions

def handle_fight(player: Player, context: PlayerContext) -> str:
    if not player.in_combat or not player.current_enemy:
        return "  You are not in combat. Explore the dungeon first."

    enemy = player.current_enemy
    p_dmg, p_crit = CombatEngine.player_attacks(player)
    e_dmg, e_crit = CombatEngine.enemy_attacks(player)

    summary = CombatEngine.combat_summary(player, p_dmg, e_dmg, p_crit, e_crit)

    # Check outcomes
    outcome_msg = ""
    if enemy["hp"] <= 0:
        xp_gain = enemy["xp"]
        gold_gain = enemy["gold"]
        player.stats.gain_xp(xp_gain)
        player.stats.gold += gold_gain
        player.in_combat = False

        loot = EventEngine.random_loot(player.stats.floor)
        player.inventory.add_item(loot)

        outcome_msg = (
            f"\n  🏆 {enemy['name']} has been slain!\n"
            f"  +{xp_gain} XP  +{gold_gain} Gold  Loot: {loot.name}\n"
            f"{player.stats_block()}"
        )
        player.current_enemy = None

    elif not player.stats.is_alive():
        player.is_alive = False
        player.in_combat = False
        outcome_msg = (
            f"\n  💀 ════════════════════════════════ 💀\n"
            f"     YOU HAVE FALLEN IN THE DARKNESS...\n"
            f"       {player.name} has met their end.\n"
            f"  💀 ════════════════════════════════ 💀\n"
            f"  Type /respawn to begin again."
        )
        sessions.broadcast(
            f"  ☠  {player.name} was slain by a {enemy['name']}...",
            exclude=player
        )

    return summary + outcome_msg


def handle_flee(player: Player, context: PlayerContext) -> str:
    if not player.in_combat:
        return "  You're not in combat."
    import random
    if random.randint(1, 100) <= 40:  # 40% flee chance
        player.in_combat = False
        player.current_enemy = None
        return (
            "  🏃 You manage to break away and flee into a dark corridor!\n"
            "  Your heart pounds... but you're safe. For now."
        )
    else:
        enemy = player.current_enemy
        e_dmg, _ = CombatEngine.enemy_attacks(player)
        return (
            f"  You try to flee, but {enemy['name']} cuts you off!\n"
            f"  You take {e_dmg} damage in the attempt! HP: {player.stats.hp}/{player.stats.max_hp}"
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