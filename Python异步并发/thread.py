from concurrent import futures
from urllib.parse import urlparse
import re
import socket
import threading


urls = [f'http://www.baidu.com/s?wd={i}' for i in range(10)]
results = []
lock = threading.Lock()


def parse(url, response):
    global results
    response = response.decode('utf8', errors='ignore')
    search = re.search(r'<title>(.*)</title>', response)
    title = search.group(1) if search else ''
    lock.acquire()
    results.append((url, title))
    lock.release()


def fetch(url):
    r = urlparse(url)
    hostname = r.hostname
    port = r.port if r.port else 80
    path = r.path if r.path else '/'
    query = r.query
    buffersize = 4096

    sock = socket.socket()
    sock.connect((hostname, port))
    get = (f'GET {path}?{query} HTTP/1.1\r\n'
           f'Connection: close\r\nHost: {hostname}\r\n\r\n')
    sock.send(get.encode('utf8'))
    response = b''
    chunk = sock.recv(buffersize)
    while chunk:
        response += chunk
        chunk = sock.recv(buffersize)
    parse(url, response)


def thread_way():
    global urls
    workers = 10
    with futures.ThreadPoolExecutor(workers) as executor:
        for target in urls:
            executor.submit(fetch, target)


if __name__ == '__main__':
    thread_way()
    print(results)
