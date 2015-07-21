class   Player:
    def __init__(self, id):
        self.id = id

    def handleEvent(self, event):
        if self not in event.to['to']:
            return
        event.sendMessage("Your character got the event : " + str(event.type),
                to=self)
