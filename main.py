from telnetServer import TelnetServer
from event import Event, EventType, Handler
from factory import Factory
from player import Player
from mud import Room
from functools import partial
import time

DEBUG = 0

def addEvents(handler, server):
    for i in server.get_new_clients():
        handler.put(Event(EventType.NEW_CONN, i))
    for i in server.get_disconnected_clients():
        handler.put(Event(EventType.DISCON, i))
    for i in server.get_messages():
        handler.put(Event(EventType.MESSAGE, i[0], i[1]))

def send(server, message, to=[], dont=[], room=[]):
    if not DEBUG and message.split(' ')[0] == "[DEBUG]":
        return
    if not isinstance(to, list):
        to = [to]
    if not isinstance(dont, list):
        dont = [dont]
    if not isinstance(room, list):
        room = [room]
    for i in to:
        if i in dont:
            continue
        server.send(i.id, message)
    for i in room:
        for j in i.components:
            if j in dont or j in to:
                continue
            server.send(j.id, message)

def populate(playerFactory, roomFactory, server, handler):
    def populateTo(event):
        to = {'to':[event.player], 'room':[], 'dont':[]}
        if event.type == EventType.NEW_CONN:
            to['room'].append(roomFactory.get(name = "no name"))
        elif event.type == EventType.UNPACK:
            to['room'].append(event.data)
        elif event.type == EventType.PACK:
            to['room'].append(event.data)
        elif event.type == EventType.SAY:
            to['room'].append(event.player.room)
        return to

    def handle(event):
        event.player = playerFactory.get(event.id, id = event.id)
        if event.data and isinstance(event.data, str):
            event.message = event.data.lstrip(' \t\r').rstrip(' \t\r').split(' ')
        elif isinstance(event.data, str):
            event.message = event.data
        else:
            event.message = None
        event.sendMessage = partial(send, server)
        event.sendEvent = handler.put
        event.to = populateTo(event)
        roomFactory.map(lambda i: i.handleEvent(event))
    return handle

server = TelnetServer("0.0.0.0", 23)
playerFactory = Factory(Player)
roomFactory = Factory(Room)
r = roomFactory.get("no name")
p = roomFactory.get("Central room")
r.exits = [p]
handler = Handler()
handler.bind(populate(playerFactory, roomFactory, server, handler), '*')

while server.update():
    addEvents(handler, server)
    handler.handleEvents()
    time.sleep(0.2)
