import datetime
from event import Event, EventType

def _say(event):
    event.type = EventType.SAY
    event.data = ' '.join(event.message)
    return event

def _tell(event):
    event.type = EventType.TELL
    event.data = (event.message[0], ' '.join(event.message[1:]))
    return event

def _help(event):
    data = """Here are all the currently implemented commands :
        - /help : this prints this help
        - /say  : say something to the current room
        - /tell : tell someone something
        - /quit : quit the mud
        - /now  : tells the current data and hour\n"""
    event.sendMessage(data, to=event.player)
    return True

def _now(event):
    return str(datetime.datetime.now())

def _quit(event):
    event.type = EventType.DISCON
    return event

_commands = {
        '/say' : _say,
        '/quit' : _quit,
        '/tell' : _tell,
        '/help' : _help,
        }

_explode_commands = {
        '/now' : _now,
        }

def parse(event):
    copy = []
    if not isinstance(event.message, list):
        event.message = event.message.split(' ')
    for i in reversed(event.message):
        try:
            copy.append(_explode_commands[i](event))
        except KeyError:
            if i in _commands:
                event.message = list(reversed(copy))
                return _commands[i](event)
            else:
                copy.append(i)
    return None
