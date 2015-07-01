class   Player():
    def __init__(self):
        self.name = None
        self.room = None

    def load(self, name, password):
        return False

    def Create(self, name, password):
        self.name = name
        return True
