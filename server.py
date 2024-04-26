import socket
import threading
from AI_MAZE import generate_dnd_maze, play
from dotenv import load_dotenv
import os
import random


load_dotenv()
PORT = int(os.getenv("PORT"))

def handle_client_connection(client_socket):
    while True:
        command = client_socket.recv(1024).decode().strip()
        if command.lower() == '/generate_maze':
            maze_scenario = generate_dnd_maze()
            client_socket.send(f"D&D Maze: {maze_scenario}".encode())

        elif command.lower() == '/roll-dice':
            rand_idx = random.randrange(len(totalclients))
            random_num = totalclients[rand_idx]
            plays_next = f"Player {str(random_num)[14:-1]}: plays next"
            print(plays_next)
            broadcast(plays_next.encode())

        elif command.startswith('/msg'):
            message = command.split(' ', 1)[1]
            broadcast_message = f"Player {client_socket.getpeername()[1]}: {message}"
            print(broadcast_message)
            broadcast(broadcast_message.encode())
        else:
            scenario_result = play(command)
            client_socket.send(f"D&D Scenario: {scenario_result}".encode())

def broadcast(message):
    for client in clients:
        client.send(message)

totalclients = []

clients = []

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('localhost', PORT))
    server_socket.listen(5)

    while True:
        client_socket, address = server_socket.accept()
        print(f"Connection from {address}")
        clients.append(client_socket)
        totalclients.append(client_socket.getpeername())
        client_handler = threading.Thread(target=handle_client_connection, args=(client_socket,))
        client_handler.start()

if __name__ == '__main__':
    main()
