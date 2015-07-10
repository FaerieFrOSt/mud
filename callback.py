import time

class   Callback():
    class   Item():
        def __init__(self, interval, func, data):
            self.interval = interval
            self.func = func
            self.data = data
            self.t = time.time()

    def __init__(self):
        self.callbacks = []

    def register(self, interval, func, data):
        self.callbacks.append(Callback.Item(interval, func, data))

    def remove(self, func):
        for i in self.callbacks:
            if i.func == func:
                del i
                return

    def run(self):
        for i in self.callbacks:
            if time.time() - i.t >= i.interval:
                i.func(i.data)
                i.t = time.time()
