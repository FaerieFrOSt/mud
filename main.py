from telnetServer import TelnetServer
from player import Player
from mud import Mud
import time

def getPlayersInRoom(players, room):
    for i in players:
        if i.room in room:
            yield i

server = TelnetServer("0.0.0.0", 23)
players = {}
mud = Mud("data.xml")
if not mud.begin:
    exit()

while server.update():
    for id in server.get_new_clients():
        players[id] = Player()
        server.send(id, "Enter your name : ")

    for id in server.get_disconnected_clients():
        name = str(id)
        try:
            name = players[id].name
            if not name:
                name = str(id)
            del(players[id])
        except KeyError:
            pass
        if name not in str(id):
            server.sendAll(name + " disconnected\n")

    for id, message in server.get_messages():
        try:
            if not players[id].name:
                players[id].create(message, mud.begin)
                server.sendAll(message + " has connected\n")
                try:
                    server.send(id, "You are in " + mud.rooms[players[id].room].name, + "\n")
                except KeyError:
                    players[id].room = mud.begin
                    server.send(id, "You have been teleported back to " + mud.begin + "\n")
                if not players[id].isVisited(mud.begin):
                    players[id].visit(mud.begin)
                    server.send(id, mud.rooms[mud.begin].desc + "\n")
                continue
            for i in getPlayersInRoom(players, players[id].room):
                server.send(i.name + " sent : " + message + "\n")
        except KeyError:
            server.send(id, "You have to log in before\n")
            server.disconnect(id)
    time.sleep(0.2)
