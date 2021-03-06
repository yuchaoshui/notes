from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from urllib.parse import urlparse
import re
import socket


selector = DefaultSelector()
stopped = False
urls = [f'http://www.baidu.com/s?wd={i}' for i in range(10)]
buffersize = 4096


class Future:

    def __init__(self):
        self.result = None
        self.callbacks = []

    def add_done_callback(self, func):
        self.callbacks.append(func)

    def set_result(self, result=None):
        self.result = result
        for func in self.callbacks:
            func(self)

    def __iter__(self):
        yield self
        return self.result


def connect(sock, address):
    global selector
    future = Future()
    sock.setblocking(False)
    try:
        sock.connect(address)
    except BlockingIOError:
        pass

    def on_connected():
        future.set_result()

    selector.register(sock.fileno(), EVENT_WRITE, on_connected)
    yield from future
    selector.unregister(sock.fileno())


def read(sock):
    future = Future()

    def on_readable():
        future.set_result(sock.recv(buffersize))

    selector.register(sock.fileno(), EVENT_READ, on_readable)
    chunk = yield from future
    selector.unregister(sock.fileno())
    return chunk


def read_all(sock):
    response = b''
    chunk = yield from read(sock)
    while chunk:
        response += chunk
        chunk = yield from read(sock)
    return response


class Spider:
    results = []

    def __init__(self, url):
        self.url = url
        r = urlparse(url)
        self.hostname = r.hostname
        self.port = r.port if r.port else 80
        self.path = r.path if r.path else '/'
        self.query = r.query
        self.response = b''
        self.sock = socket.socket()

    def parse(self):
        response = self.response.decode('utf8', errors='ignore')
        search = re.search(r'<title>(.*)</title>', response)
        title = search.group(1) if search else ''
        self.results.append((self.url, title))

    def fetch(self):
        global urls
        global stopped
        yield from connect(self.sock, (self.hostname, self.port))
        get = (f'GET {self.path}?{self.query} HTTP/1.1\r\n'
               f'Connection: close\r\nHost: {self.hostname}\r\n\r\n')
        self.sock.send(get.encode())
        self.response = yield from read_all(self.sock)
        urls.remove(self.url)
        stopped = True if not urls else False
        self.parse()


class Task:

    def __init__(self, corotine):
        self.corotine = corotine
        future = Future()
        self.step(future)

    def step(self, future):
        try:
            next_future = self.corotine.send(future.result)
        except StopIteration:
            return
        next_future.add_done_callback(self.step)


def event_loop():
    global stopped
    global selector
    while not stopped:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback()


if __name__ == '__main__':
    for target in urls:
        spider = Spider(target)
        Task(spider.fetch())
    event_loop()
    print(Spider.results)
