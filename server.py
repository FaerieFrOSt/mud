import socket
import select
import time

# state
_READ_STATE_NORMAL = 1
_READ_STATE_COMMAND = 2
_READ_STATE_SUBNEG = 3

# telnet protocol
_TN_INTERPRET_AS_COMMAND = 255
_TN_ARE_YOU_THERE = 246
_TN_WILL = 251
_TN_WONT = 252
_TN_DO = 253
_TN_DONT = 254
_TN_SUBNEGOTIATION_START = 250
_TN_SUBNEGOTIATION_END = 240

# create TCP socket and set it up
listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

# bind it to port 23
listenSocket.bind(("0.0.0.0", 23))

# non blocking mode
listenSocket.setblocking(False)

# start listening
listenSocket.listen(1)

clients = []

def cleanup(client, data):
    state = _READ_STATE_NORMAL
    message = None
    for c in data:
        if state == _READ_STATE_NORMAL:
            if ord(c) == _TN_INTERPRET_AS_COMMAND:
                state = _READ_STATE_COMMAND
            elif c == "\n":
                message = str(client[3])
                client[3] = ""
            elif c == "\x08":
                client[3] = client[3][:-1]
            else:
                client[3] += c
        elif state == _READ_STATE_COMMAND:
            if ord(c) == _TN_SUBNEGOTIATION_START:
                state = _READ_STATE_SUBNEG
            elif ord(c) in (_TN_WILL, _TN_WONT, _TN_DO, _TN_DONT):
                state = _READ_STATE_COMMAND
            else:
                state = _READ_STATE_NORMAL
        elif state == _READ_STATE_SUBNEG:
            if ord(c) == _TN_SUBNEGOTIATION_END:
                state = _READ_STATE_NORMAL
    return message

def send(client, data):
    try:
        client[0].sendall(bytearray(data, "latin1"))
    except KeyError:
        pass
    except socket.error:
        clients.remove(client)

def check_new_connections():
    rlist, wlist, xlist = select.select([listenSocket], [], [], 0)
    # if socket not in readable list, then no data available
    if listenSocket not in rlist:
        return
    joinedSocket, addr = listenSocket.accept()
    joinedSocket.setblocking(False)
    clients.append([joinedSocket, addr[0], time.time(), ""])

def check_alive():
    for i in clients:
        if time.time() - i[2] < 5.0:
            continue
        send(i, "\x00")

def check_messages():
    messages = []
    for i in clients:
        rlist, wlist, xlist = select.select([i[0]], [], [], 0)
        if i[0] not in rlist :
            continue
        try:
            # read data
            data = i[0].recv(4096).decode("latin1")
            message = cleanup(i, data)
            if message:
                message = message.strip()
                messages.append(message)
        except socket.error:
            clients.remove(i)
    return messages

while True:
    check_new_connections()
    check_alive()
    messages = check_messages()
    for i in messages:
        print(i)
        if "exit" in i:
            break
