# notes
从Python同步的方式开始，逐步演化Python异步原理，从同步到异步的过程分别如下,文件内容为：使用基础的socket编写爬虫爬取百度的多个搜索的结果。

# sync.py
简单的同步方式顺序爬取指定url列表。


# process.py
在一个程序内，依次执行10次太耗时，那开10个同样的程序执行就可以解决问题。此时当进程数量大于CPU核心数量时，进程切换是必然需要的，同时支持的任务规模较小。


# thread.py
由于线程的线程的数据结构比进程更轻量级，并且同一个进程可以容纳多个线程，所以可以使用多线程解决并发问题。多线程也是有问题的，因为多线程有一个GIL锁：同一时刻一个进程中只有一个进程在运行，并且在线程切换时还资源消耗大，而协程的切换则是在线程内部，所以协程优于线程。


# no_blocking.py
和sync.py的不同在两个地方，`sock.setblocking(False)`表示该socket的后续操作都不阻塞，在`sock.connect((hostname, port))`时，建立连接是一个耗时操作，所以需要不断的尝试发送数据`sock.send(get)`，直到成功为止(因为不知道连接什么时候建立好)，`chunk = sock.recv(buffersize)`也是同样的道理(在非阻塞情况下不知道什么时候可以接受数据，所以需要不断循环)，在不断尝试的过程中CPU是空闲的，没有利用好这段时间，所以和sync.py时间是差不多的。


# callback.py
callback 能够充分利用no_blocking的CPU空闲，把IO事件的监听交给OS来完成。所以需要我们把数据的发送和读取封装成独立的函数，并使用epoll将封装好的函数注册到selector，一旦epoll监听到了文件描述符读就绪或者写就绪，就通知应用程序，让应用程序调用之前注册好了的处理函数。整个过程中，根据不同的URL不断的产生新的文件描述符并注册selector，所以程序中需要一个循环程序来判断selector的状态是否就绪，就绪以后就直接调用下一步操作（刚刚注册的函数：发送数据、接收数据）。


# generator.py
基于生成器的协程方式是一个比较优的解决方案，它利用生成器的挂起、唤醒特性实现并发功能，为了解决上面回调的逻辑混乱问题，做如下改进：

- Future对象
Future对象用来存放未来的结果。一个URL对应一个任务，这个任务从开始到获得结果结束的整个过程中，有耗时操作，所以需要将这个任务挂起，挂起的同时将这个任务到此时为止的执行结果保存到Future里面，下次唤醒此任务时将结果send给生成器。

- Task对象
Task对象对应到一个具体的任务，每一个url对应一个task对象，它控制着任务的执行。

- Fetch方法
它是实际的任务逻辑，fetch方法里面一旦需要挂起就创建一个新的Future对象，然后yield挂起，并将下次唤醒时要执行的函数注册到selector，注册的函数里面包含了：当文件描述符就绪时将获取的结果赋值给Future对象，然后继续执行后续操作。

- 事件循环
同回调一样，也需要一个事件循环来处理已就绪的文件描述符。

- 主程序
主程序不断创建新的任务，整个调用链如下
    - 1、进入for循环，执行第一次for，创建一个Spider的生成器，将其传递给Task任务，由Task任务激活生成器，直到生成器遇到一个yield为止，生成器创建Future对象、注册selector回调函数并将Future对象返回给Task，由Task将下次的函数保存到Future对象。
    - 2、进入第二次for循环，和第一步一样，遇到第一个yield以后被挂起。
    - 3、直到所有的任务都启动，这个过程很快，因为所有的操作都没有IO。
    - 4、进入事件的循环，判断是否前面启动的任务有描述符就绪的任务，就处理。
    - 5、注意：这个Future对象被唤醒的时机是由selector的文件描述符来确定的，当文件描述就绪时就会调用注册的函数，从而会被唤醒。

# yield_from.py
yield_from的出现简化了生成器的语法，主要有两个功能：
- 让嵌套生成器不必通过循环迭代yield，而是直接yield from。
- 在子生成器和原生成器的调用者之间打开双向通道，两者可以直接通信。

然后将和业务无关的代码抽象出来，就形成了yield from版本的并发。

# async_await.py
- asyncio是Python 3.4 引入的异步I/O框架，提供了基于协程做异步I/O编写单线程并发代码的基础设施。其核心组件有事件循环（Event Loop）、协程(Coroutine）、任务(Task)、未来对象(Future)以及其他一些扩充和辅助性质的模块。
- 装饰器@asyncio.coroutine用于装饰使用了yield from的函数，以标记其为协程。
- async/await语法是对yield from的优化，称之为原生协程。async/await 和 yield from这两种风格的协程底层复用共同的实现，而且相互兼容。

# socket_server_sync.py
一个同步的简单socket server

# socket_server_async.py
一个异步的简单socket server

# socket_client.py
socket 客户端

