import logging
from typing import Dict

from server.ai.context_manager import PlayerContext
from server.game.player import Player
from server.handlers.admin_handler import (
    handle_help,
    handle_new_floor,
    handle_roll,
    handle_who,
)
from server.handlers.chat_handler import handle_chat, handle_whisper
from server.handlers.combat_handler import handle_fight, handle_flee, handle_respawn
from server.handlers.inventory_handler import handle_inventory, handle_use_item
from server.handlers.movement import handle_movement
from server.session_manager import sessions

logger = logging.getLogger(__name__)


class CommandRouter:
    """Routes player text input to the appropriate handler."""

    def route(self, raw_input: str, player: Player, context: PlayerContext) -> str:
        raw = raw_input.strip()
        if not raw:
            return ""

        cmd, _, args = raw.partition(" ")
        cmd = cmd.lower()

        # Dead player guard
        if not player.is_alive and cmd not in ("/respawn", "/help"):
            return "  You are dead. Type /respawn to return."

        # Combat guard — use .get() so mypy never indexes Optional[Dict] directly
        if player.in_combat:
            enemy: Dict = player.current_enemy or {}
            enemy_name = enemy.get("name", "your enemy")
            if cmd not in ("/fight", "/flee", "/use", "/inv", "/help", "/stats"):
                return f"  You are in combat with {enemy_name}! Fight or flee!"

        try:
            return self._dispatch(cmd, args, player, context)
        except Exception as e:
            logger.exception(f"Command error for player {player.name}: {e}")
            return "  An error occurred. The dungeon magic wavers..."

    def _dispatch(
        self, cmd: str, args: str, player: Player, context: PlayerContext
    ) -> str:
        # Movement
        if cmd in ("/n", "/s", "/e", "/w", "/north", "/south", "/east", "/west"):
            direction = cmd.lstrip("/")
            return handle_movement(player, direction, context)

        # Combat
        elif cmd == "/fight":
            return handle_fight(player, context)
        elif cmd == "/flee":
            return handle_flee(player, context)
        elif cmd == "/respawn":
            return handle_respawn(player)

        # Inventory
        elif cmd == "/inv":
            return handle_inventory(player)
        elif cmd == "/use":
            if not args:
                return "  Usage: /use <item name>"
            return handle_use_item(player, args, context)

        # Social
        elif cmd == "/msg":
            return handle_chat(player, args)
        elif cmd == "/w":
            return handle_whisper(player, args)
        elif cmd == "/who":
            return handle_who(player)
        elif cmd == "/leaderboard":
            return sessions.leaderboard()

        # Game
        elif cmd == "/stats":
            return player.stats_block()
        elif cmd == "/roll":
            return handle_roll(player, args)
        elif cmd == "/new_floor":
            return handle_new_floor(player, context)
        elif cmd == "/look":
            return (
                context.dungeon_summary
                or "The dungeon stretches before you in all directions."
            )
        elif cmd == "/help":
            return handle_help(player)

        # Free-form AI input (no slash)
        elif not cmd.startswith("/"):
            full_input = (cmd + " " + args).strip()
            from server.ai.gemini_client import gemini

            response = gemini.generate(full_input, history=context.get_history())
            context.add_exchange(full_input, response)
            return response

        else:
            return f"  Unknown command '{cmd}'. Type /help for a list of commands."


router = CommandRouter()