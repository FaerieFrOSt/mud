from telnetServer import TelnetServer
from event import Event, EventType, Handler
from factory import Factory
from player import Player
from mud import Room
from functools import partial
import time

def addEvents(handler, server):
    for i in server.get_new_clients():
        handler.put(Event(EventType.NEW_CONN, i))
    for i in server.get_disconnected_clients():
        handler.put(Event(EventType.DISCON, i))
    for i in server.get_messages():
        handler.put(Event(EventType.MESSAGE, i[0], i[1]))

def send(server, message, to=[], dont=[], room=[]):
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
    def handle(event):
        event.player = playerFactory.get(id = event.id)
        event.sendMessage = partial(send, server)
        event.sendEvent = handler.put
        event.to = {
                'to'   : [event.player],
                'room' : [],
                'dont' : [],
                }
        roomFactory.map(lambda i: i.handleEvent(event))
    return handle

def newConnection(playerFactory, room, server, handler):
    def handle(event):
        event.player = playerFactory.get(event.id)
        event.to = {
                'to'   : [event.player],
                'room' : [room],
                'dont' : [],
                }
        event.sendMessage = partial(send, server)
        event.sendEvent = handler.put
        room.handleEvent(event)
    return handle

server = TelnetServer("0.0.0.0", 23)
playerFactory = Factory(Player)
roomFactory = Factory(Room)
noRoom = roomFactory.get("no name", name = "no name")
handler = Handler()
handler.bind(newConnection(playerFactory, noRoom, server, handler), EventType.NEW_CONN)
handler.bind(populate(playerFactory, roomFactory, server, handler), EventType.DISCON)
handler.bind(populate(playerFactory, roomFactory, server, handler), EventType.MESSAGE)

while server.update():
    addEvents(handler, server)
    handler.handleEvents()
    time.sleep(0.2)
