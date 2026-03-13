import logging
from typing import List, Optional

import google.generativeai as genai

from server.ai.prompts import SYSTEM_PROMPT
from server.config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """Singleton wrapper around the Gemini API."""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        genai.configure(api_key=config.GEMINI_API_KEY)
        self._model = genai.GenerativeModel(
            model_name=config.AI_MODEL,
            system_instruction=SYSTEM_PROMPT,
        )
        self._initialized = True
        logger.info(f"Gemini client initialized with model: {config.AI_MODEL}")

    def generate(self, prompt: str, history: Optional[List] = None) -> str:
        """Generate a response, optionally with conversation history."""
        try:
            if history:
                chat = self._model.start_chat(history=history)
                response = chat.send_message(prompt)
            else:
                response = self._model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "The dungeon magic falters... (AI error, please try again)"


gemini = GeminiClient()