from server.game.player import Player
from server.session_manager import sessions

def handle_chat(player: Player, message: str) -> str:
    """Broadcast a chat message to all players."""
    if not message.strip():
        return "  Usage: /msg <your message>"
    broadcast = f"\n  💬 [{player.name}]: {message}"
    sessions.broadcast(broadcast, exclude=player)
    return f"  💬 [You → All]: {message}"

def handle_whisper(player: Player, args: str) -> str:
    """Send a private message to a specific player."""
    parts = args.split(" ", 1)
    if len(parts) < 2:
        return "  Usage: /w <player_name> <message>"
    target_name, message = parts[0], parts[1]
    target = next(
        (p for p in sessions.all_players() if p.name.lower() == target_name.lower()),
        None
    )
    if not target:
        return f"  Player '{target_name}' is not online."
    target.send(f"\n  🔔 [Whisper from {player.name}]: {message}")
    return f"  🔔 [Whisper to {target_name}]: {message}"