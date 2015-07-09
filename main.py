from telnetServer import TelnetServer
from player import Player
from mud import Mud
from worker import Worker
from busevent import BusEvent
from mysql import Mysql
import time

server = TelnetServer("0.0.0.0", 23)
mud = Mud("data.xml")
bus = BusEvent()
mysql = Mysql('localhost', 'mud', 'root', 'vive-moi')
if not mysql.ok:
    print("Error while connecting to mysql")
    exit()
if not mud.begin:
    print("Error while loading data for mud")
    exit()
worker = Worker(mud, server, bus, mysql)

while server.update():
    worker.connections()
    worker.disconnections()
    worker.messages()
    time.sleep(0.2)
