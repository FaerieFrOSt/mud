import datetime

class   Parser:
    def __init__(self):
        self.explode_commands = {
                '/now'  : self.now,
                }
        self.commands = {
                '/say'  : self.say,
                }

    def say(self, message):
        pass

    def now(self, message):
        return str(datetime.datetime.now())
    
    def explode(self, message):
        copy = []
        if not isinstance(message, list):
            message = message.split(' ')
        for i in reversed(message):
            try:
                copy.append(self.explode_commands[i](message))
            except KeyError:
                if i in self.commands:
                    self.commands[i](list(reversed(copy)))
                    return
                else:
                    copy.append(i)
        self.send("send", "Command not found\n", to=player)
