import socket


def main(host, port):
    client = socket.socket()
    client.connect((host, port))

    while True:
        data = input('>')
        if not data:
            break
        client.send(data.encode())
        chunk = client.recv(8192)
        if not chunk:
            break
        print(chunk)


if __name__ == '__main__':
    main('127.0.0.1', 8888)
