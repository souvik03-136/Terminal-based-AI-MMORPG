import threading
import sys
import logging
from client.connection import Connection
from client.input_handler import InputHandler
from client.display import colorize

logging.basicConfig(level=logging.WARNING)

def receive_loop(conn: Connection):
    """Background thread: continuously print server messages."""
    while True:
        try:
            data = conn.recv(4096)
            if not data:
                print("\n  [Disconnected from server]")
                sys.exit(0)
            print(colorize(data), end="", flush=True)
        except Exception:
            break

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dungeon Explorer Client")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=4000,  help="Server port")
    args = parser.parse_args()

    conn = Connection(host=args.host, port=args.port)
    if not conn.connect():
        sys.exit(1)

    # Start receive thread
    recv_thread = threading.Thread(target=receive_loop, args=(conn,), daemon=True)
    recv_thread.start()

    handler = InputHandler()

    try:
        while True:
            user_input = handler.get_input()
            if not user_input:
                continue
            if user_input == "/quit":
                print("\n  Farewell, adventurer.\n")
                break
            conn.send(user_input)
    except KeyboardInterrupt:
        print("\n  Farewell, adventurer.\n")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
