class   Parser():
    def __init__(self, bus):
        self.send = bus.send
        self.commands = {
                '/say'  : self.say,
                '/tell' : self.tell,
                '/quit' : self.quit,
                '/help' : self.help,
                '/now'  : self.now,
                }

    def help(self, player, message):
        data = """Here is the list of the commands :
        help - print this help,
        say  - say something,
        tell - tell someone something
        quit - quit the mud\n"""
        return {data : ('to', player)}, False

    def say(self, player, message):
        data = player.name + " says '" + ' '.join(message) + "'\n"
        data = "You say '" + ' '.join(message) + "'\n"

    def quit(self, player, message):
        try:
            self.send("quit", player.id)
        except KeyError:
            pass

    def tell(self, player, message):
        return

    def now(self, player, message):
        return

    def explode(self, player, message):
        data = []
        copy = message
        for i in message:
            try:
                tmp, c = self.commands[i](player, message)
                data.append(tmp)
                if not c:
                    break
            except KeyError:
                pass
