import sys
from threading import Thread
is_py2 = sys.version[0] == '2'
if is_py2:
    import Queue as queue
else:
    import queue as queue


class ThreadPool:
    def __init__(self, num_threads, queue_size):
        self.queue = queue.Queue(queue_size)
        self.num = num_threads
        self.threads = []
        for i in range(0, num_threads):  # Start each thread and add to the list
            self.threads.append(ThreadWorker(self.queue))

    def addTask(self, func, *args, **kargs):
        self.queue.put((func, args, kargs))

    def endThreads(self):
        for i in range(0, self.num):
            self.addTask(None)
        for i in range(0, self.num):
            self.threads[i].join()

    def wait_completion(self):
        self.tasks.join()


class ThreadWorker(Thread):
    def __init__(self, _queue):
        self.tasks = _queue
        self.on = True
        Thread.__init__(self)
        self.start()  # Start thread

    def run(self):
        while self.on:
            func, args, kargs = self.tasks.get()
            self.on = func(*args, **kargs)
