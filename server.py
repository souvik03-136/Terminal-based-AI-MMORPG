# server.py

import socket
import threading
from AI_MAZE import generate_dnd_maze, play

def handle_client_connection(client_socket):
    while True:
        command = client_socket.recv(1024).decode().strip()
        if command.lower() == '/generate_maze':
            maze_scenario = generate_dnd_maze()
            client_socket.send(f"D&D Maze: {maze_scenario}".encode())
        else:
            scenario_result = play(command)
            client_socket.send(f"D&D Scenario: {scenario_result}".encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', 8888))
    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")
        client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
