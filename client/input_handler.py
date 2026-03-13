import sys

class InputHandler:
    """Handles user input with basic validation."""

    ALIASES = {
        "n": "/n", "s": "/s", "e": "/e", "w": "/w",
        "north": "/north", "south": "/south",
        "east": "/east", "west": "/west",
        "fight": "/fight", "f": "/fight",
        "flee": "/flee",
        "inv": "/inv", "i": "/inv",
        "help": "/help", "h": "/help",
        "stats": "/stats",
        "quit": "/quit", "exit": "/quit", "q": "/quit",
    }

    def get_input(self) -> str:
        try:
            raw = input("\n  > ").strip()
        except (EOFError, KeyboardInterrupt):
            return "/quit"

        if not raw:
            return ""

        # Expand shorthand aliases
        lower = raw.lower()
        if lower in self.ALIASES:
            return self.ALIASES[lower]

        # Ensure slash commands start with /
        if raw.startswith("/") or raw.startswith(" "):
            return raw

        # Otherwise treat as free-form (AI chat or action)
        return raw