import random
from typing import Dict, Tuple
from server.game.player import Player
from server.game.dice import Dice

class CombatEngine:
    """Turn-based combat system."""

    @staticmethod
    def player_attacks(player: Player) -> Tuple[int, bool]:
        """Player attacks current enemy. Returns (damage, is_crit)."""
        roll = Dice.roll_d20()
        is_crit = roll == 20
        base_dmg = player.stats.attack
        if is_crit:
            dmg = base_dmg * 2
        elif roll >= 8:
            dmg = base_dmg + Dice.roll_d6()
        else:
            dmg = max(1, base_dmg // 2)

        enemy = player.current_enemy
        enemy_def = enemy.get("defense", 0)
        actual = max(1, dmg - enemy_def // 2)
        enemy["hp"] -= actual
        return actual, is_crit

    @staticmethod
    def enemy_attacks(player: Player) -> Tuple[int, bool]:
        """Enemy attacks player. Returns (damage_taken, is_crit)."""
        enemy = player.current_enemy
        roll = Dice.roll_d20()
        is_crit = roll == 20
        base_dmg = enemy.get("attack", 10)
        if is_crit:
            dmg = base_dmg * 2
        elif roll >= 8:
            dmg = base_dmg + Dice.roll_d6()
        else:
            dmg = max(1, base_dmg // 2)

        actual = player.stats.take_damage(dmg)
        return actual, is_crit

    @staticmethod
    def combat_summary(player: Player, p_dmg: int, e_dmg: int,
                       p_crit: bool, e_crit: bool) -> str:
        enemy = player.current_enemy
        crit_str_p = " ⚡ CRITICAL STRIKE!" if p_crit else ""
        crit_str_e = " ⚡ CRITICAL HIT!" if e_crit else ""
        alive = "alive" if player.stats.is_alive() else "DEFEATED"
        enemy_status = f"HP: {max(0, enemy['hp'])}" if enemy["hp"] > 0 else "SLAIN"
        return (
            f"  ⚔  You strike {enemy['name']} for {p_dmg} dmg!{crit_str_p}\n"
            f"  🗡  {enemy['name']} hits you for {e_dmg} dmg!{crit_str_e}\n"
            f"  Enemy — {enemy_status}   |   You — HP: {player.stats.hp}/{player.stats.max_hp} ({alive})"
        )