from collections import deque
from typing import List, Dict

class PlayerContext:
    """Maintains a rolling window of conversation history per player."""

    def __init__(self, max_messages: int = 20):
        self.max_messages = max_messages
        self._history: deque = deque(maxlen=max_messages)
        self.dungeon_summary: str = ""  # compressed world state

    def add_exchange(self, user_msg: str, ai_response: str):
        self._history.append({"role": "user", "parts": [user_msg]})
        self._history.append({"role": "model", "parts": [ai_response]})

    def get_history(self) -> List[Dict]:
        return list(self._history)

    def set_dungeon_summary(self, summary: str):
        self.dungeon_summary = summary

    def clear(self):
        self._history.clear()
        self.dungeon_summary = ""