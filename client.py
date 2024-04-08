import socket

def main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(('localhost', 8888))

    while True:
        command = input("Enter your command: ")
        client_socket.send(command.encode())
        response = client_socket.recv(1024).decode()
        print(response)

if __name__ == '__main__':
    main()
