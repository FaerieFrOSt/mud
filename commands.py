import datetime

class   Parser():
    def __init__(self, bus):
        self.send = bus.send
        self.explode_commands = {
                '/now'  : self.now,
                }
        self.commands = {
                '/say'  : self.say,
                '/tell' : self.tell,
                '/quit' : self.quit,
                '/help' : self.help,
                '/look' : self.look,
                '/goto' : self.goto,
                }

    def goto(self, player, message):
        if len(message) < 1:
            self.send("send", "Usage : /goto direction\n", to=player)
            return
        for i in player.room.exits:
            if i.direction == message[0]:
                r = player.room
                self.send("move", player, i.to)
                self.send("look", player)
                self.send("send", player.name + " has left the room\n",
                        rooms=r)
                self.send("send", player.name + " has entered the room\n",
                        dont=player, rooms=player.room)
                return
        self.send("send", message[0] + " is not a valid exit\n", to=player)

    def look(self, player, message):
        l = self.send("room", player.room)
        desc = l["room"].desc
        if len(message) > 0 and message[0] == "false":
            desc = ""
        if not l:
            return
        data = """You are in {0}.
{1}

""".format(l["room"].name, desc)
        data = data + "The exits are : " + ', '.join(str(i) for i in l["room"].exits) + "\n"
        data = data + ', '.join(str(a) for a in l["players"])
        if len(l["players"]) > 1:
            data += " are here.\n"
        elif len(l["players"]) == 1:
            data += " is here.\n"
        else:
            data += "There isn't anyone here.\n"
        self.send("send", data, to=player)

    def help(self, player, message):
        data = """Here is the list of the commands :
        help - print this help,
        say  - say something,
        tell - tell someone something
        quit - quit the mud
        now  - print the date
        look - print the description and who is here
        goto - go somewhere else\n"""
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
        t = self.send("findPlayer", message[0])
        if not t:
            self.send("send", message[0] + " is not connected right now\n",
                    to=player)
            return
        self.send("send", data, to=t)
        data = "You tell " + message[0] + " '" + ' '.join(message[1:]) + "'\n"
        self.send("send", data, to=player)
        
    def now(self, player, message):
        return str(datetime.datetime.now())

    def explode(self, player, message):
        copy = []
        if not isinstance(message, list):
            message = message.split(' ')
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
