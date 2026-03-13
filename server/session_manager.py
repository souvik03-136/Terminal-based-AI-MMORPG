import logging
from typing import Dict, Optional
from server.game.player import Player

logger = logging.getLogger(__name__)

class SessionManager:
    """Tracks all active player sessions."""

    def __init__(self):
        self._players: Dict[str, Player] = {}  # player_id → Player
        self._socket_map: Dict[int, str] = {}   # socket fileno → player_id

    def add_player(self, player: Player):
        self._players[player.player_id] = player
        self._socket_map[player.socket.fileno()] = player.player_id
        logger.info(f"Player '{player.name}' joined. ID: {player.player_id}")

    def remove_player(self, player: Player):
        self._players.pop(player.player_id, None)
        self._socket_map.pop(player.socket.fileno(), None)
        logger.info(f"Player '{player.name}' disconnected.")

    def get_player_by_socket(self, sock) -> Optional[Player]:
        pid = self._socket_map.get(sock.fileno())
        return self._players.get(pid)

    def all_players(self) -> list:
        return list(self._players.values())

    def count(self) -> int:
        return len(self._players)

    def broadcast(self, message: str, exclude: Player = None):
        for player in self._players.values():
            if exclude and player.player_id == exclude.player_id:
                continue
            player.send(message)

    def leaderboard(self) -> str:
        if not self._players:
            return "  No adventurers online."
        sorted_players = sorted(
            self._players.values(),
            key=lambda p: (p.stats.level, p.stats.xp),
            reverse=True
        )
        lines = ["\n  ╔═══ LEADERBOARD ════════════════╗"]
        for i, p in enumerate(sorted_players[:10], 1):
            lines.append(
                f"  ║ {i:>2}. {p.name:<12} LVL{p.stats.level:<3} Floor {p.stats.floor} ║"
            )
        lines.append("  ╚════════════════════════════════╝")
        return "\n".join(lines)

sessions = SessionManager()