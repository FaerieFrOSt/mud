class   Player():
    def __init__(self):
        self.name = None
        self.room = None
        self.visited = []
        self.id = None

    def load(self, name):
        return False

    def create(self, id, name, room):
        self.name = name
        self.room = room
        self.id = id
        return True

    def visit(self, room):
        self.visited.append(room)

    def isVisited(self, room):
        return room in self.visited
