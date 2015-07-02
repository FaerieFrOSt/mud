class   Player():
    def __init__(self):
        self.name = None
        self.room = None
        self.visited = []

    def load(self, name):
        return False

    def create(self, name, room):
        self.name = name
        self.room = room
        return True

    def visit(self, room):
        self.visited.append(room)

    def isVisited(self, room):
        return room in self.visited
