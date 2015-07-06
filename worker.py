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
        self.parser = Parser(bus)

    def room(self, room):
        data = {}
        data["room"] = self.mud.rooms[room]
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
        return self.mud.rooms[player.room]

    def sendRoom(self, player):
        self.send("You are in " + self.getRoom(player).name + "\n",
                to=player)

    def sendExits(self, player):
        self.send("Exits : " + ' '.join(self.getRoom(player).exits) + '\n',
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
            self.sendExits(player)
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
            if not player.isVisited(player.room):
                self.sendDesc(player)
                self.sendExits(player)
                player.visit(player.room)
            message = message.lstrip(' \t\r')
            message = message.rstrip(' \t\r')
            message = message.split(' ')
            if len(message) < 1:
                self.sendCommandLine(player)
                continue
            self.parser.explode(player, message)
            self.sendCommandLine(player)
