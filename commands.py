import datetime

class   Parser():
    def __init__(self, findPlayer, bus):
        self.send = bus.send
        self.find = findPlayer
        self.explode_commands = {
                '/now'  : self.now,
                }
        self.commands = {
                '/say'  : self.say,
                '/tell' : self.tell,
                '/quit' : self.quit,
                '/help' : self.help,
                }

    def help(self, player, message):
        data = """Here is the list of the commands :
        help - print this help,
        say  - say something,
        tell - tell someone something
        quit - quit the mud\n"""
        self.send("send", data, to=player)

    def say(self, player, message):
        data = player.name + " says '" + ' '.join(message) + "'\n"
        self.send("send", data, dont=player, rooms=player.room)
        data = "You say '" + ' '.join(message) + "'\n"
        self.send("send", data, to=player)

    def quit(self, player, message):
        try:
            self.send("send", player.name + " has left\n", dont=player,
                    rooms=player.room)
            self.send("send", "See you soon!\n", to=player)
            self.send("quit", player.id)
        except KeyError:
            pass

    def tell(self, player, message):
        data = player.name + " tells you '" + ' '.join(message[1:]) + "'\n"
        t = self.find(message[0])
        if not t:
            self.send("send", message[0] + " is not connected right now\n",
                    to=player)
            return
        self.send("send", data, to=t)
        data = "You tell " + message[0] + " '" + ' '.join(message) + "'\n"
        self.send("send", data, to=player)
        
    def now(self, player, message):
        return str(datetime.datetime.now())

    def explode(self, player, message):
        copy = []
        for i in reversed(message):
            try:
                copy.append(self.explode_commands[i](player, message))
            except KeyError:
                if i in self.commands:
                    self.commands[i](player, list(reversed(copy)))
                    return
                else:
                    copy.append(i)
        self.send("send", "Command not found\n", to=player)
