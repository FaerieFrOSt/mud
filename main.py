from telnetServer import TelnetServer

server = TelnetServer("0.0.0.0", 23)

while server.update():
    continue
