# notes
从Python同步的方式开始，逐步演化Python异步原理，从同步到异步的过程分别如下,文件内容为：使用基础的socket编写爬虫爬取百度的多个搜索的结果。

# sync.py
简单的同步方式一次爬取指定url列表。

# no_blocking.py
和sync.py的不同在两个地方，`sock.setblocking(False)`表示该socket的后续操作都不阻塞，在`sock.connect((hostname, port))`时，建立连接是一个耗时操作，所以需要不断的尝试发送数据`sock.send(get)`，直到成功为止，`chunk = sock.recv(buffersize)`也是同样的道理，在不断尝试的过程中CPU是空闲的，没有利用好这段时间，所以和sync.py时间是差不多的。

