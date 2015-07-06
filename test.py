import datetime

def say(message):
    print(' '.join(message))

def tell(message):
    print(message[0])
    print(' '.join(message[1:]))

def now(message):
    return str(datetime.datetime.now())

commands_explode = {
        '/now' : now,
        }

commands = {
        '/say' : say,
        '/tell' : tell,
        }

message = '/tell marc hello dear world. It is now /now and I\'m really cool about it /now /now'

message = message.split(' ')
copy = []
for i in reversed(message):
    try:
        copy.append(commands_explode[i](message))
    except KeyError:
        if i in commands:
            commands[i](list(reversed(copy)))
        else:
            copy.append(i)
