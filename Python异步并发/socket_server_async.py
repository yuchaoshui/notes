from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
import socket


class EventLoop:

    def __init__(self, selector=None):
        self.selector = selector if selector else DefaultSelector()

    def run_forever(self):
        while True:
            events = self.selector.select()
            for key, mask in events:
                if mask == EVENT_READ:
                    callback = key.data  # means on_read or on_accept
                    callback(key.fileobj)
                else:
                    callback, msg = key.data  # means on_write
                    callback(key.fileobj, msg)


class EchoServer:

    def __init__(self, host, port, loop):
        self.host = host
        self.port = port
        self.loop = loop
        self.sock = socket.socket()
        self.buffersize = 4096

    def on_accept(self, sock):
        conn, address = sock.accept()
        print('accepted', conn, 'from', address)
        conn.setblocking(False)
        self.loop.selector.register(conn, EVENT_READ, self.on_read)

    def on_read(self, conn):
        msg = conn.recv(self.buffersize)
        if msg:
            print('echoing', repr(msg), 'to', conn)
            self.loop.selector.modify(conn, EVENT_WRITE, (self.on_write, msg))
        else:
            print('closing', conn)
            self.loop.selector.unregister(conn)
            conn.close()

    def on_write(self, conn, msg):
        conn.sendall(msg)
        self.loop.selector.modify(conn, EVENT_READ, self.on_read)

    def run(self):
        self.sock.bind((self.host, self.port))
        self.sock.setblocking(False)
        self.sock.listen(128)
        print(f'Running on http://{self.host}:{self.port}/')
        self.loop.selector.register(self.sock, EVENT_READ, self.on_accept)
        self.loop.run_forever()


event_loop = EventLoop()
echo_server = EchoServer('localhost', 8888, event_loop)
echo_server.run()
