from threading import Thread
class Worker(Thread):
    def __init__(self, _queue):
        self.tasks = _queue
        self.on = True
        Thread.__init__(self)
        self.start()  # Start thread

    def run(self):
        while self.on:
            func, args, kargs = self.tasks.get()
            self.on = func(*args, **kargs)