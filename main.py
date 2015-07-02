from telnetServer import TelnetServer
from player import Player
from mud import Mud
from worker import Worker
import time

server = TelnetServer("0.0.0.0", 23)
mud = Mud("data.xml")
if not mud.begin:
    exit()
worker = Worker(mud, server)

while server.update():
    worker.connections()
    worker.disconnections()
    worker.messages()
    time.sleep(0.2)
