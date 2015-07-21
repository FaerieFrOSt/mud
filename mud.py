from event import Container, EventType

class   Room(Container):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

    def handleEvent(self, event):
        if self in event.to['room']:
            if event.type == EventType.NEW_CONN:
                self.pack(event.player)
        super().handleEvent(event)
