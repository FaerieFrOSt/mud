class   BusEvent():
    def __init__(self):
        self.registered = {}

    def register(self, name, func):
        self.registered[name] = func

    def send(self, name, *args, **kwargs):
        try:
            return self.registered[name](*args, **kwargs)
        except KeyError:
            pass

