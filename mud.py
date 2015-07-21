from event import Container, EventType

class   Room(Container):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return self.name

    def handleEvent(self, event):
        unpack = []
        if self in event.to['room']:
            if event.type == EventType.NEW_CONN:
                self.pack(event.player)
            elif event.type == EventType.UNPACK:
                unpack.append(event.player)
                event.sendMessage(str(event.player) + " has left the room\n",
                        dont=event.player, room=self)
            elif event.type == EventType.PACK:
                event.sendMessage(str(event.player) + " has entered the room\n",
                        room=self)
                self.pack(event.player)
        super().handleEvent(event)
        for i in unpack:
            self.unpack(i)
