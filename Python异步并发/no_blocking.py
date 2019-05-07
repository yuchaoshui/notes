from urllib.parse import urlparse
import re
import socket


urls = [f'http://www.baidu.com/s?wd={i}' for i in range(10)]
results = []


def parse(url, response):
    global results
    response = response.decode('utf8', errors='ignore')
    search = re.search(r'<title>(.*)</title>', response)
    title = search.group(1) if search else ''
    results.append((url, title))


def fetch(url):
    r = urlparse(url)
    hostname = r.hostname
    port = r.port if r.port else 80
    path = r.path if r.path else '/'
    query = r.query
    buffersize = 4096

    sock = socket.socket()
    sock.setblocking(False)
    try:
        sock.connect((hostname, port))
    except BlockingIOError:
        pass

    get = (f'GET {path}?{query} HTTP/1.1\r\n'
           f'Connection: close\r\nHost: {hostname}\r\n\r\n')
    get = get.encode('utf8')

    while True:
        try:
            sock.send(get)
            break
        except OSError:
            pass

    response = b''
    while True:
        try:
            chunk = sock.recv(buffersize)
            while chunk:
                response += chunk
                chunk = sock.recv(buffersize)
            break
        except OSError:
            pass

    parse(url, response)


if __name__ == '__main__':
    for target in urls:
        fetch(target)
    print(results)
