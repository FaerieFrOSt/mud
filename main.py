from telnetServer import TelnetServer
import time

server = TelnetServer("0.0.0.0", 23)

while server.update():
    for id in server.get_new_clients():
        print("A new client connected(" + str(id) + ")")
    for id in server.get_disconnected_clients():
        print("A client disconnected(" + str(id) + ")")
    for id, message in server.get_messages():
        print(str(id) + " sent : " + message)
    time.sleep(0.2)
