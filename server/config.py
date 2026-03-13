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
    AI_MODEL: str = "gemini-1.5-flash"
    MAX_CONTEXT_MESSAGES: int = 20  # per player rolling window

    @classmethod
    def validate(cls):
        if not cls.GEMINI_API_KEY:
            raise EnvironmentError(
                "GEMINI_API_KEY is not set. Please configure your .env file."
            )

config = Config()