import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    PORT: int = int(os.getenv("PORT", 4000))
    HOST: str = os.getenv("HOST", "localhost")
    MAX_PLAYERS: int = int(os.getenv("MAX_PLAYERS", 10))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    BUFFER_SIZE: int = 4096
    # google.genai uses "gemini-2.0-flash" — no "-latest" suffix needed
    AI_MODEL: str = "gemini-2.0-flash"
    MAX_CONTEXT_MESSAGES: int = 20

    @classmethod
    def validate(cls) -> None:
        """
        Validates server config at startup.
        A missing or invalid GEMINI_API_KEY is NOT fatal —
        the server runs in offline mode with handcrafted content.
        """
        if not cls.GEMINI_API_KEY:
            import logging

            logging.getLogger(__name__).warning(
                "GEMINI_API_KEY not set — starting in offline mode. "
                "Add a valid key to .env to enable AI narration."
            )


config = Config()