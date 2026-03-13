"""Terminal color and formatting utilities."""

class Color:
    RESET   = "\033[0m"
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    RED     = "\033[91m"
    GREEN   = "\033[92m"
    YELLOW  = "\033[93m"
    BLUE    = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN    = "\033[96m"
    WHITE   = "\033[97m"
    GRAY    = "\033[90m"

def colorize(text: str) -> str:
    """Apply color codes based on content markers."""
    replacements = {
        "⚔": Color.YELLOW + "⚔" + Color.RESET,
        "💀": Color.RED + "💀" + Color.RESET,
        "💰": Color.YELLOW + "💰" + Color.RESET,
        "🏆": Color.CYAN + "🏆" + Color.RESET,
        "⚠": Color.RED + "⚠" + Color.RESET,
        "❤": Color.RED + "❤" + Color.RESET,
        "✨": Color.MAGENTA + "✨" + Color.RESET,
        "📢": Color.CYAN + "📢" + Color.RESET,
        "💬": Color.GREEN + "💬" + Color.RESET,
        "🔔": Color.MAGENTA + "🔔" + Color.RESET,
        "🎲": Color.YELLOW + "🎲" + Color.RESET,
        "🔻": Color.RED + "🔻" + Color.RESET,
        "🔍": Color.CYAN + "🔍" + Color.RESET,
        "🏃": Color.GREEN + "🏃" + Color.RESET,
        "🗡": Color.YELLOW + "🗡" + Color.RESET,
    }
    for symbol, colored in replacements.items():
        text = text.replace(symbol, colored)
    return text