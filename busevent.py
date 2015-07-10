from collections import defaultdict

class   BusEvent():
    def __init__(self):
        self.registered = defaultdict(list)

    def register(self, name, func):
        self.registered[name].append(func)

    def send(self, name, *args, **kwargs):
        try:
            ret = []
            for i in self.registered[name]:
                a = i(*args, **kwargs)
                if a:
                    ret.append(a)
            if len(ret) == 1:
                return ret[0]
            return ret
        except KeyError as e:
            print("BusEvent error : " + str(e) + " not registered")
