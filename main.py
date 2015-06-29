from telnetServer import TelnetServer
import time

server = TelnetServer("0.0.0.0", 23)

while server.update():
    for id in server.get_new_clients():
        print("A new client connected(" + str(id) + ")")
        server.sendAllExcept(id, "A new client connected(" + str(id) + ")\n")

    for id in server.get_disconnected_clients():
        print("A client disconnected(" + str(id) + ")")
        server.sendAllExcept(id, "A client disconnected(" + str(id) + ")\n")
    for id, message in server.get_messages():
        print(str(id) + " sent : " + message)
        server.sendAll(str(id) + " sent : " + message + "\n")
    time.sleep(0.2)
