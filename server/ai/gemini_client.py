"""
AI Client
=========
Uses the current google-genai SDK (google.genai).
If the API key is missing, empty, or invalid, automatically falls back
to the offline FallbackEngine — no crash, fully playable either way.
"""

import logging
from typing import List, Optional

from server.config import config

logger = logging.getLogger(__name__)


class GeminiClient:
    """
    Singleton AI client.

    Priority:
      1. Google Gemini 2.0 Flash   (if GEMINI_API_KEY is set and valid)
      2. Offline FallbackEngine    (automatic — no config needed)
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._client = None
        self._fallback = None
        self._using_fallback = False

        if config.GEMINI_API_KEY:
            self._try_init_gemini()
        else:
            self._init_fallback("No GEMINI_API_KEY found in environment")

        self._initialized = True

    # ------------------------------------------------------------------
    # Initialisation helpers
    # ------------------------------------------------------------------

    def _try_init_gemini(self) -> None:
        try:
            from google import genai  # new SDK — replaces google.generativeai

            self._client = genai.Client(api_key=config.GEMINI_API_KEY)

            # Lightweight probe — catches invalid / revoked keys immediately
            # rather than letting the first real game call blow up in a player's face
            self._client.models.generate_content(
                model=config.AI_MODEL,
                contents="ping",
            )
            logger.info(f"✅  Gemini client ready — model: {config.AI_MODEL}")

        except Exception as e:
            err = str(e)
            if "API_KEY_INVALID" in err or "API key not valid" in err:
                self._init_fallback(
                    "Invalid API key — check GEMINI_API_KEY in your .env"
                )
            else:
                self._init_fallback(f"Gemini init failed: {e}")

    def _init_fallback(self, reason: str) -> None:
        from server.ai.fallback_engine import fallback

        self._client = None
        self._fallback = fallback
        self._using_fallback = True
        logger.warning(
            f"⚠   AI fallback mode active — {reason}\n"
            "    Dungeon Explorer will run with handcrafted offline content.\n"
            "    Set a valid GEMINI_API_KEY in .env to enable AI narration."
        )

    # ------------------------------------------------------------------
    # Public interface
    # ------------------------------------------------------------------

    @property
    def mode(self) -> str:
        return "offline" if self._using_fallback else "gemini"

    def generate(self, prompt: str, history: Optional[List] = None) -> str:
        """Generate a response. Uses Gemini if available, fallback otherwise."""
        if self._using_fallback and self._fallback is not None:
            return self._fallback.generate(prompt, history)

        try:
            from google.genai import types

            # Build a content list, prepending any conversation history
            contents = []
            if history:
                for msg in history:
                    role = msg.get("role", "user")
                    parts = msg.get("parts", [])
                    text = parts[0] if parts else ""
                    contents.append(
                        types.Content(role=role, parts=[types.Part(text=text)])
                    )

            contents.append(
                types.Content(role="user", parts=[types.Part(text=prompt)])
            )

            response = self._client.models.generate_content(
                model=config.AI_MODEL,
                contents=contents,
            )
            return response.text.strip()

        except Exception as e:
            err = str(e)
            if "API_KEY_INVALID" in err or "API key not valid" in err:
                # Switch permanently so we don't keep hammering a dead key
                logger.error("API key invalid — switching permanently to offline mode")
                self._init_fallback("API key rejected at runtime")
            else:
                logger.error(f"Gemini API error: {e} — using fallback for this request")

            from server.ai.fallback_engine import fallback
            return fallback.generate(prompt, history)


gemini = GeminiClient()