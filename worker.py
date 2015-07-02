from telnetServer import TelnetServer
from mud import Mud
from player import Player

class   Worker():
    def __init__(self, mud, server):
        self.players = {}
        self.mud = mud
        self.server = server
        commands = {
            'say'  : self.say,
            'tell' : self.tell,
            }

    def say(self, player, message):
        self.sendToRoom(player, ' '.join(message[1:]))

    def tell(self, player, message):
        self.send(player.id, "not implemented\n")

    def connections(self):
        for id in self.server.get_new_clients():
            self.players[id] = Player()
            self.server.send(id, "Enter your name : ")

    def disconnections(self):
        for id in self.server.get_disconnected_clients():
            player = None
            try:
                player = self.players[id]
                del(self.players[id])
                self.sendToRoom(player.room, player.name +
                        " disconnected\n")
            except KeyError:
                pass

    def getPlayersInRoom(self, room):
        for j, i in list(self.players.items()):
            if i.room in room:
                yield i

    def sendToRoom(self, room, message):
        for i in self.getPlayersInRoom(room):
            self.server.send(i.id, message)

    def getRoom(self, player):
        return self.mud.rooms[player.room]

    def sendRoom(self, player):
        self.server.send(player.id,
                "You are in " + self.getRoom(player).name + "\n")

    def sendDesc(self, player):
        if player.isVisited(player.room):
            return
        player.visit(player.room)
        self.send(player.id, self.getRoom(player).desc + "\n")

    def loadOrCreate(self, id, message):
        player = self.players[id]
        if player.name:
            return player
        player.create(id, message, self.mud.begin)
        try:
            self.sendRoom(player)
        except KeyError:
            player.room = self.mud.begin
            self.server.send(id,
                "You have been teleported back to "
                + player.room + "\n")
            self.sendDesc(player)
        return player

    def messages(self):
        for id, message in self.server.get_messages():
            player = None
            try:
                player = self.loadOrCreate(id, message)
                self.sendToRoom(player.room, player.name +
                        " has connected\n")
                continue
            except KeyError:
                server.send(id, "You have to log in before\n")
                server.disconnect(id)
            if not player:
                continue
            message = message.lstrip([' ', '\t', '\r'])
            message = message.rstrip([' ', '\t', '\r'])
            message = message.split(' ')
            try:
                self.commands[message[0]](player, message)
            except KeyError:
                self.send(id, "This is not a known command, try again\n")
