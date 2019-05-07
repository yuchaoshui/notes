from selectors import DefaultSelector, EVENT_WRITE, EVENT_READ
from urllib.parse import urlparse
import re
import socket


selector = DefaultSelector()
stopped = False
urls = [f'http://www.baidu.com/s?wd={i}' for i in range(10)]


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
        self.buffersize = 4096
        self.sock = socket.socket()

    def parse(self):
        response = self.response.decode('utf8', errors='ignore')
        search = re.search(r'<title>(.*)</title>', response)
        title = search.group(1) if search else ''
        self.results.append((self.url, title))

    def fetch(self):
        global selector
        self.sock.setblocking(False)
        try:
            self.sock.connect((self.hostname, self.port))
        except BlockingIOError:
            pass
        selector.register(self.sock.fileno(), EVENT_WRITE, self.connected)

    def connected(self, key):
        global selector
        selector.unregister(key.fd)
        get = (f'GET {self.path}?{self.query} HTTP/1.1\r\n'
               f'Connection: close\r\nHost: {self.hostname}\r\n\r\n')
        self.sock.send(get.encode())
        selector.register(key.fd, EVENT_READ, self.read_response)

    def read_response(self, key):
        global selector
        global stopped
        chunk = self.sock.recv(self.buffersize)
        if chunk:
            self.response += chunk
        else:
            selector.unregister(key.fd)
            urls.remove(self.url)
            stopped = True if not urls else False
            self.parse()


def event_loop():
    global selector
    global stopped
    while not stopped:
        events = selector.select()
        for key, mask in events:
            callback = key.data
            callback(key)


if __name__ == '__main__':
    for target in urls:
        spider = Spider(target)
        spider.fetch()
    event_loop()
    print(Spider.results)
