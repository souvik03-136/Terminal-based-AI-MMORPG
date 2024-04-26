import socket
from dotenv import load_dotenv
import os


load_dotenv()
PORT = int(os.getenv("PORT"))


def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', PORT))
    while True:
        command = input("Enter your command: ")
        client_socket.send(command.encode())
        response = client_socket.recv(1024).decode()
        print(response)

if __name__ == '__main__':
    main()
