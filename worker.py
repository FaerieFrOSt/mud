from telnetServer import TelnetServer
from mud import Mud
from player import Player
from commands import Parser

class   Worker():
    def __init__(self, mud, server, bus, mysql):
        self.players = {}
        self.mud = mud
        self.server = server
        self.mysql = mysql
        self.bus = bus
        bus.register("send", self.send)
        #bus.register("echo", self.server.echo)
        bus.register("quit", self.quit)
        bus.register("findPlayer", self.findPlayer)
        bus.register("room", self.room)
        bus.register("getRoomByName", self.getRoomByName)
        bus.register("move", self.move)
        bus.register("look", self.printEnter)
        self.parser = Parser(bus)

    def broadcast(self, message):
        for j, i in self.players.items():
            self.send(message, to=i)

    def getRoomByName(self, name):
        try:
            return self.mud.rooms[name]
        except KeyError:
            pass

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
        self.players[id].save()
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
            self.players[id] = Player(self.mysql, id, self.bus, self.mud.begin)
            self.send("Enter your name : ", to=self.players[id])

    def disconnections(self):
        for id in self.server.get_disconnected_clients():
            player = None
            try:
                player = self.players[id]
                player.save()
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

    def messages(self):
        for id, message in self.server.get_messages():
            player = None
            try:
                player = self.players[id]
            except KeyError:
                self.server.send(id, "You must first login!\n")
                self.server.disconnect(id)
            message = message.lstrip(' \t\r')
            message = message.rstrip(' \t\r')
            message = message.split(' ')
            player.treat(message)
