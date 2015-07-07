from telnetServer import TelnetServer
from mud import Mud
from player import Player
from commands import Parser

class   Worker():
    def __init__(self, mud, server, bus):
        self.players = {}
        self.mud = mud
        self.server = server
        bus.register("send", self.send)
        bus.register("quit", self.quit)
        bus.register("findPlayer", self.findPlayer)
        bus.register("room", self.room)
        bus.register("move", self.move)
        bus.register("look", self.printEnter)
        self.parser = Parser(bus)

    def printEnter(self, player):
        if player.isVisited(player.room):
            self.parser.explode(player, "/look false")
        else:
            self.parser.explode(player, "/look")
            player.visit(player.room)

    def move(self, player, name):
        player.room = self.mud.rooms[name]

    def room(self, room):
        data = {}
        data["room"] = self.mud.rooms[room.name]
        data["players"] = []
        for i in self.getPlayersInRoom(room):
            data["players"].append(i)
        return data

    def quit(self, id):
        del(self.players[id])
        self.server.disconnect(id)

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

    def findPlayer(self, name):
        for i, j in self.players.items():
            if j.name == name:
                return j
        return None

    def getPlayersInRoom(self, room):
        for j, i in list(self.players.items()):
            if i.room == room:
                yield i

    def getRoom(self, player):
        return self.mud.rooms[player.room.name]

    def sendCommandLine(self, player):
        self.send(">", to=player)

    def loadOrCreate(self, id, message):
        player = self.players[id]
        if player.name:
            return player, True
        player.create(message, self.mud.begin)
        try:
            self.printEnter(player)
            self.send(player.name + " has connected\n", dont=player,
                    rooms=player.room)
        except KeyError:
            player.room = self.mud.begin
            self.send("You have been teleported back to " + player.room
                    + "\n", to=player)
            self.sendExits(player)
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
            message = message.lstrip(' \t\r')
            message = message.rstrip(' \t\r')
            message = message.split(' ')
            if len(message) < 1:
                self.sendCommandLine(player)
                continue
            self.parser.explode(player, message)
            self.sendCommandLine(player)
