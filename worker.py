from telnetServer import TelnetServer
from mud import Mud
from player import Player

class   Worker():
    def __init__(self, mud, server):
        self.players = {}
        self.mud = mud
        self.server = server
        self.commands = {
                'help' : self.help,
                'say'  : self.say,
                'tell' : self.tell,
                'quit' : self.quit,
                }

    def help(self, player, message):
        data = """Here is the list of the commands :
        help - print this help,
        say  - say something,
        tell - tell someone something
        quit - quit the mud\n"""
        self.send(data, to=player)

    def say(self, player, message):
        data = player.name + " says '" + ' '.join(message[1:]) + "'\n"
        self.send(data, dont=player, rooms=player.room)
        data = "You say '" + ' '.join(message[1:]) + "'\n"
        self.send(data, to=player)

    def quit(self, player, message):
        try:
            id = player.id
            self.send(player.name + " has disconnected\n", dont=player,
                    rooms=player.room)
            self.send("See you soon!\n", to=player)
            del(self.players[id])
            self.server.disconnect(id)
        except KeyError:
            pass

    def tell(self, player, message):
        self.send("Not implemented\n", to=player)

    def send(self, message, to=[], dont=[], rooms=[]):
        if not isinstance(to, list):
            to = [to]
        if not isinstance(dont, list):
            dont = [dont]
        if not isinstance(rooms, list):
            rooms = [rooms]
        for i in to:
            if i in dont:
                continue
            self.server.send(i.id, message)
        for room in rooms:
            for i in self.getPlayersInRoom(room):
                if i in dont:
                    continue
                self.server.send(i.id, message)

    def connections(self):
        for id in self.server.get_new_clients():
            self.players[id] = Player(id)
            self.send("Enter your name : ", to=self.players[id])

    def disconnections(self):
        for id in self.server.get_disconnected_clients():
            player = None
            try:
                player = self.players[id]
                del(self.players[id])
                self.send(player.name + " disconnected\n", dont=player,
                        room=player.room)
            except KeyError:
                pass

    def getPlayersInRoom(self, room):
        for j, i in list(self.players.items()):
            if i.room in room:
                yield i

    def getRoom(self, player):
        return self.mud.rooms[player.room]

    def sendRoom(self, player):
        self.send("You are in " + self.getRoom(player).name + "\n",
                to=player)

    def sendDesc(self, player):
        if player.isVisited(player.room):
            return
        player.visit(player.room)
        self.send(self.getRoom(player).desc + "\n", to=player)

    def sendCommandLine(self, player):
        self.send(">", to=player)

    def loadOrCreate(self, id, message):
        player = self.players[id]
        if player.name:
            return player, True
        player.create(message, self.mud.begin)
        try:
            self.sendRoom(player)
            if not player.isVisited(player.room):
                self.sendDesc(player)
                player.visit(player.room)
            self.send(player.name + " has connected\n", dont=player,
                    rooms=player.room)
        except KeyError:
            player.room = self.mud.begin
            self.send("You have been teleported back to " + player.room
                    + "\n", to=player)
        return player, False

    def messages(self):
        for id, message in self.server.get_messages():
            player = None
            try:
                player, b = self.loadOrCreate(id, message)
                if not b:
                    self.sendCommandLine(player)
                    continue
            except KeyError:
                self.send(id, "You have to log in before\n", to=player)
                self.server.disconnect(id)
            if not player:
                continue
            if not player.isVisited(player.room):
                self.sendDesc(player)
                player.visit(player.room)
            message = message.lstrip(' \t\r')
            message = message.rstrip(' \t\r')
            message = message.split(' ')
            if len(message) < 1:
                self.sendCommandLine(player)
                continue
            try:
                self.commands[message[0]](player, message)
                self.sendCommandLine(player)
            except KeyError:
                self.send("This is not a known command, try again\n",
                        to=player)
