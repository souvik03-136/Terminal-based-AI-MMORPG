import logging
import socket
from typing import Optional

from server.config import config

logger = logging.getLogger(__name__)


class Connection:
    def __init__(self, host: Optional[str] = None, port: Optional[int] = None):
        self.host: str = host or config.HOST
        self.port: int = port or config.PORT
        self._socket: Optional[socket.socket] = None

    def connect(self) -> bool:
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.host, self.port))
            logger.info(f"Connected to {self.host}:{self.port}")
            return True
        except ConnectionRefusedError:
            print(f"\n  ERROR: Cannot connect to {self.host}:{self.port}")
            print("  Make sure the server is running first.\n")
            return False

    def send(self, message: str) -> None:
        if self._socket:
            self._socket.send(message.encode())

    def recv(self, bufsize: int = 4096) -> str:
        if self._socket:
            data = self._socket.recv(bufsize)
            return data.decode("utf-8", errors="replace")
        return ""

    def close(self) -> None:
        if self._socket:
            self._socket.close()