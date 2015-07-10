import time

class   Callback():
    class   Item():
        def __init__(self, interval, func):
            self.interval = interval
            self.func = func
            self.t = time.time()

    def __init__(self):
        self.callbacks = []

    def register(self, interval, func):
        self.callbacks.append(Callback.Item(interval, func))

    def update(self, interval, func):
        for i in self.callbacks:
            if i.func == func:
                i.interval = interval

    def remove(self, func):
        for i in self.callbacks:
            if i.func == func:
                del i
                return

    def run(self):
        for i in self.callbacks:
            if time.time() - i.t >= i.interval:
                i.func()
                i.t = time.time()
