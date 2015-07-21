from telnetServer import TelnetServer
from event import Event, EventType, Handler
from factory import Factory
from player import Player
from mud import Room
import time

def addEvents(handler, server):
    for i in server.get_new_clients():
        handler.put(Event(EventType.NEW_CONN, i))
    for i in server.get_disconnected_clients():
        handler.put(Event(EventType.DISCON, i))
    for i in server.get_messages():
        handler.put(Event(EventType.MESSAGE, i[0], i[1]))

def populate(playerFactory, roomFactory):
    def handle(event):
        event.player = playerFactory.get(id = event.id)
        roomFactory.map(lambda i: i.handleEvent(event))
    return handle

def newConnection(playerFactory, room):
    def handle(event):
        event.player = playerFactory.get(event.id)
        room.handleEvent(event)
    return handle

server = TelnetServer("0.0.0.0", 23)
playerFactory = Factory(Player)
roomFactory = Factory(Room)
noRoom = roomFactory.get("no name", name = "no name")
handler = Handler()
handler.bind(newConnection(playerFactory, noRoom), EventType.NEW_CONN)
handler.bind(populate(playerFactory, roomFactory), EventType.DISCON)
handler.bind(populate(playerFactory, roomFactory), EventType.MESSAGE)

while server.update():
    addEvents(handler, server)
    handler.handleEvents()
    time.sleep(0.2)
