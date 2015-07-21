from event import EventType, Event

class   Player:
    _NAME_ASK = 1
    _PASSWORD_ASK = 2
    _NORMAL = 3

    def __init__(self, id):
        self.id = id
        self.name = None
        self.room = None
        self.state = Player._NAME_ASK
        self.func = {
                Player._NAME_ASK : self.defName,
                Player._NORMAL : self.digest,
                }

    def defName(self, event):
        if event.type == EventType.NEW_CONN:
            event.sendMessage("Enter your name : ", to=self)
            self.room = event.to['room'][0]
        elif event.type == EventType.MESSAGE:
            self.name = event.message[0]
            event.sendMessage("Welcome to this mud!\n", to=self)
            event.sendEvent(Event(EventType.UNPACK, self.id, self.room))
            event.sendEvent(Event(EventType.PACK, self.id, self.room.exits[0]))
            self.state = Player._NORMAL

    def digest(self, event):
        if event.type == EventType.MESSAGE:
            event.sendMessage("Command not reconized!\n", to=self)
            return True
        elif event.type == EventType.UNPACK and self.room.name != "no name":
            event.sendMessage("You left " + str(self.room) + "\n", to=self)
            self.room = None
        elif event.type == EventType.PACK:
            self.room = event.to['room'][0]
            event.sendMessage("You entered " + str(self.room) + "\n", to=self)
            return True

    def commandLine(self):
        return "> "

    def handleEvent(self, event):
        if self not in event.to['to']:
            return
        event.sendMessage("[DEBUG] Your character got the event : " + str(event.type)
                + "\n", to=self)
        if event.type == EventType.MESSAGE and len(event.message) < 1:
            event.sendMessage(self.commandLine(), to=self)
            return
        if self.func[self.state](event):
            event.sendMessage(self.commandLine(), to=self)

    def __str__(self):
        return self.name
