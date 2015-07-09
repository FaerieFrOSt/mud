class   Player():
    _STATE_NORMAL = 0
    _STATE_ANSWER = 1
    _STATE_NAME = 2
    _STATE_PASS = 3

    def __init__(self, mysql, id, bus, begin):
        self.name = None
        self.room = None
        self.visited = []
        self.id = id
        self.mysql = mysql
        self.send = bus.send
        self.state = self._STATE_NAME
        self.funcs = [self.normal, self.answer, self.defName, self.setPass]
        self.mudBegin = begin
        self.passwd = None

    def normal(self, message):
        self.send("parse", self, message)
        return True

    def answer(self, message):
        pass

    def defName(self, message):
        if len(message) < 1 or message[0] == "":
            self.send("send", "Please enter a valid name for your character : ",
                    to=self)
            return
        self.name = message[0]
        self.send("send", "Character created. Enter your password : ", to=self)
        self.send("echo", self.id, False)
        self.state = self._STATE_PASS

    def setPass(self, message):
        if len(message) < 1 or message[0] == "":
            self.send("send", "Please enter a valid password : ", to=self)
            return
        self.state = self._STATE_NORMAL
        self.passwd = message[0]
        self.send("echo", self.id, True)
        self.send("send", "You're ready to play! Welcome!\n", to=self)
        self.room = self.mudBegin
        self.send("look", self)
        self.send("send", self.name + " has entered the room\n",
                dont=self, rooms=self.room)
        return True

    def treat(self, message):
        if len(message) < 1 and self.state == _STATE_NORMAL:
            self.send("send", self.commandLine(), to=player)
            return
        if not self.funcs[self.state](message):
            return
        self.send("send", ">", to=self)

    def visit(self, room):
        self.visited.append(room)

    def isVisited(self, room):
        return room in self.visited

    def __str__(self):
        return self.name
