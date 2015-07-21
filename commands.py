import datetime
from event import Event, EventType

def _say(event):
    event.type = EventType.SAY
    event.data = ' '.join(event.message[1:])
    event.to['to'] = [event.player]
    event.to['room'] = [event.player.room]
    return event

def _now(event):
    return str(datetime.datetime.now())

_commands = {
        '/say' : _say,
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
                event.data = list(reversed(copy))
                return _commands[i](event)
            else:
                copy.append(i)
    return None
