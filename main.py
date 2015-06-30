from telnetServer import TelnetServer
from player import Player
import time

server = TelnetServer("0.0.0.0", 23)
players = {}

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
                players[id].name = message
                server.sendAll(message + " has connected\n")
                continue
            server.sendAll(players[id].name + " sent : " + message + "\n")
        except KeyError:
            pass
    time.sleep(0.2)
