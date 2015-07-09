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

    def save(self):
        if not self.name or not self.passwd:
            return
        if len([i for i in self.mysql.getEntry("select name from users where name='" + self.name + "'")]) < 1:
            self.mysql.writeEntry("insert into users (name, password, room) values ('" + self.name + "', '" + self.passwd + "', '" + self.room.name + "')")
        else:
            self.mysql.writeEntry("update users set room='" + self.room.name + "' where name='" + self.name + "'")

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
        res = self.mysql.getEntry("select * from users where name='"
                + message[0] + "'")
        a = [i for i in res]
        if len(a) == 1:
            self.send("send", "Character found. Enter your password : ",
                    to=self)
        elif len(a) < 1:
            self.send("send", "Character created. Enter your password : ", to=self)
            self.send("echo", self.id, False)
        self.state = self._STATE_PASS

    def setPass(self, message):
        if len(message) < 1 or message[0] == "":
            self.send("send", "Please enter a valid password : ", to=self)
            return
        res = self.mysql.getEntry("select * from users where name='"
                + self.name + "'")
        a = [i for i in res]
        if len(a) < 1 or (len(a) == 1 and a[0]["password"] == message[0]):
            self.passwd = message[0]
            if len(a) < 1:
                self.room = self.mudBegin
                self.save()
            if len(a) == 1:
                self.room = self.send("getRoomByName", a[0]["room"])
            self.send("echo", self.id, True)
            self.send("send", "You're ready to play! Welcome!\n", to=self)
        elif len(a) == 1 and a[0]["password"] != message[0]:
            self.send("send", "This is the wrong password, try again : ",
                    to=self)
            return
        self.send("look", self)
        self.send("send", self.name + " has entered the room\n",
                dont=self, rooms=self.room)
        self.state = self._STATE_NORMAL
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
