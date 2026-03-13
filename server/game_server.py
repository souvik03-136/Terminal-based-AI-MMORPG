import logging
import socket
import threading
from typing import Optional

from server.ai.context_manager import PlayerContext
from server.ai.gemini_client import gemini
from server.ai.prompts import MAZE_GENERATION_PROMPT
from server.command_router import router
from server.config import config
from server.game.player import Player
from server.game.world import world
from server.session_manager import sessions

logger = logging.getLogger(__name__)

WELCOME_BANNER = r"""
  ██████╗ ██╗   ██╗███╗   ██╗ ██████╗ ███████╗ ██████╗ ███╗   ██╗
  ██╔══██╗██║   ██║████╗  ██║██╔════╝ ██╔════╝██╔═══██╗████╗  ██║
  ██║  ██║██║   ██║██╔██╗ ██║██║  ███╗█████╗  ██║   ██║██╔██╗ ██║
  ██║  ██║██║   ██║██║╚██╗██║██║   ██║██╔══╝  ██║   ██║██║╚██╗██║
  ██████╔╝╚██████╔╝██║ ╚████║╚██████╔╝███████╗╚██████╔╝██║ ╚████║
  ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝ ╚═════╝ ╚══════╝ ╚═════╝ ╚═╝  ╚═══╝
               EXPLORER  ·  A Terminal-Based AI MMORPG
  ═══════════════════════════════════════════════════════════════
"""

BANNER_AI = "  ✨  Mode: AI Narration (Gemini)  — the dungeon breathes with intelligence.\n"
BANNER_OFFLINE = (
    "  ⚔   Mode: Offline  — handcrafted dungeons, no API key required.\n"
    "  Tip: Set GEMINI_API_KEY in .env to unlock AI narration.\n"
)


def handle_client(client_socket: socket.socket, address: tuple) -> None:
    logger.info(f"New connection from {address}")
    player: Optional[Player] = None

    try:
        mode_line = BANNER_AI if gemini.mode == "gemini" else BANNER_OFFLINE
        client_socket.send((WELCOME_BANNER + mode_line).encode())
        client_socket.send("  Enter your adventurer's name: ".encode())

        name_raw = client_socket.recv(256).decode().strip()
        name = name_raw[:16] if name_raw else f"Stranger_{address[1]}"

        player = Player(name=name, address=address, socket=client_socket)
        context = PlayerContext(max_messages=config.MAX_CONTEXT_MESSAGES)
        sessions.add_player(player)

        # Generate opening floor
        if gemini.mode == "offline":
            from server.ai.fallback_engine import fallback

            opening = fallback.generate_floor(1)
        else:
            opening = gemini.generate(MAZE_GENERATION_PROMPT)

        world.set_floor_description(1, opening)
        context.set_dungeon_summary(opening[:300])
        context.add_exchange("Player enters the dungeon", opening)

        sessions.broadcast(f"\n  📢 {name} has entered the dungeon!", exclude=player)

        player.send(
            f"\n  Welcome, {name}. Your legend begins here.\n\n"
            f"{opening}\n"
            f"{player.stats_block()}\n"
            f"  Type /help to see all commands.\n"
        )

        while True:
            try:
                data = client_socket.recv(config.BUFFER_SIZE)
                if not data:
                    break
                command = data.decode("utf-8", errors="replace").strip()
                if not command:
                    continue

                logger.debug(f"[{name}] > {command}")
                response = router.route(command, player, context)
                if response:
                    player.send(response)

            except ConnectionResetError:
                break
            except UnicodeDecodeError:
                player.send("  (Unreadable input — try plain text)")

    except Exception as e:
        logger.exception(f"Error handling client {address}: {e}")
    finally:
        _cleanup(client_socket, player)


def _cleanup(client_socket: socket.socket, player: Optional[Player] = None) -> None:
    if player:
        sessions.remove_player(player)
        sessions.broadcast(f"\n  📢 {player.name} has left the dungeon.")
        logger.info(f"Player '{player.name}' disconnected.")
    try:
        client_socket.close()
    except Exception:
        pass


class GameServer:
    def __init__(self) -> None:
        self._server_socket: Optional[socket.socket] = None

    def start(self) -> None:
        config.validate()
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind((config.HOST, config.PORT))
        self._server_socket.listen(config.MAX_PLAYERS)

        logger.info(f"Dungeon Explorer server started on {config.HOST}:{config.PORT}")
        logger.info(f"AI mode: {gemini.mode}")
        logger.info(f"Max players: {config.MAX_PLAYERS}")

        try:
            while True:
                client_socket, address = self._server_socket.accept()
                thread = threading.Thread(
                    target=handle_client,
                    args=(client_socket, address),
                    daemon=True,
                )
                thread.start()
        except KeyboardInterrupt:
            logger.info("Server shutting down...")
        finally:
            self._server_socket.close()