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
        self.bindings[eventType] = func

    def handleEvents(self):
        while not self.empty():
            e = self.get()
            try:
                self.bindings[e.type](e)
            except KeyError:
                pass
        
