from telnetServer import TelnetServer
from player import Player
from mud import Mud
from worker import Worker
from busevent import BusEvent
import time

server = TelnetServer("0.0.0.0", 23)
mud = Mud("data.xml")
bus = BusEvent()
if not mud.begin:
    exit()
worker = Worker(mud, server, bus)

while server.update():
    worker.connections()
    worker.disconnections()
    worker.messages()
    time.sleep(0.2)
