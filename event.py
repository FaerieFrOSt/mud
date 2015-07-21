from enum import Enum
import queue

class   EventType(Enum):
    NEW_CONN = 1
    DISCON = 2
    MESSAGE = 3
    SEND_TO = 4
    CHANGE_ROOM = 5
    UNPACK = 6
    PACK = 7
    SAY = 8
    TELL = 9

class   Event:
    def __init__(self, type = None, id = None, data = None):
        self.type = type
        self.id = id
        self.data = data

class   Container:
    def __init__(self):
        self.components = []

    def pack(self, component):
        self.components.append(component)

    def unpack(self, component):
        self.components.remove(component)

    def getComponent(self, id):
        for i in self.components:
            if i.id == id:
                return i

    def handleEvent(self, event):
        for i in self.components:
            i.handleEvent(event)

class   Handler(queue.Queue):
    def __init__(self):
        super().__init__()
        self.bindings = {}

    def bind(self, func, eventType):
        if eventType == '*':
            for i in EventType:
                self.bindings[i] = func
        else:
            self.bindings[eventType] = func

    def handleEvents(self):
        ret = None
        while not self.empty():
            e = self.get(block = False)
            if e.type == EventType.DISCON:
                ret = e.id
            try:
                self.bindings[e.type](e)
            except KeyError:
                print(str(e.type) + " has no binding")
        return ret 
