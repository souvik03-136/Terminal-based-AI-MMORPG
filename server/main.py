import logging
from server.config import config
from server.game_server import GameServer

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL, logging.INFO),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

def main():
    server = GameServer()
    server.start()

if __name__ == "__main__":
    main()