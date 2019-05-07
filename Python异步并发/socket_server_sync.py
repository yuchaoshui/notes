import socket


class EchoServer:

    def __init__(self, host, port):
        self.sock = socket.socket()
        self.host = host
        self.port = port
        self.buffersize = 4096

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.listen(1)
        print(f'Running on http://{self.host}:{self.port}/')
        while True:
            conn, address = self.sock.accept()
            print('accepted', conn, 'from', address)
            while True:
                chunk = conn.recv(self.buffersize)
                if not chunk:
                    break
                print('echoing', repr(chunk), 'to', conn)
                conn.sendall(chunk)


echo_server = EchoServer('localhost', 8888)
echo_server.run()
