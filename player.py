class   Player:
    def __init__(self, id):
        self.id = id

    def handleEvent(self, event):
        print(str(self.id) + " had an event : " + str(event.type))
