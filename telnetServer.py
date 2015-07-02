import socket
import time
import select

class   TelnetServer():
    # telnet protocol
    _TN_INTERPRET_AS_COMMAND = 255
    _TN_ARE_YOU_THERE = 246
    _TN_WILL = 251
    _TN_WONT = 252
    _TN_DO = 253
    _TN_DONT = 254
    _TN_SUBNEGOTIATION_START = 250
    _TN_SUBNEGOTIATION_END = 240

    # server events
    _EVENT_NEW_CLIENT = 1
    _EVENT_CLIENT_DISCONNECTED = 2
    _EVENT_MESSAGE = 3

    class   Client():
        def __init__(self, socket, address):
            self.socket = socket
            self.address = address
            self.lastCheck = time.time()
            self.buffer = ""

    def __init__(self, ip, port):
        self.clients = {}
        self.nextId = 0
        self.events = []
        self.newEvents = []
        self.listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.listenSocket.bind((ip, port))
        self.listenSocket.setblocking(False)
        self.listenSocket.listen(1)

    def shutdown(self):
        for client in self.clients.values():
            client.socket.shutdown()
            client.socket.close()
        self.listenSocket.close()

    def disconnect(self, client):
        try:
            self.clients[client].socket.shutdown()
            self.clients[client].socket.close()
        except KeyError:
            pass

    def update(self):
        self._check_new_connections()
        self._check_disconnected()
        self._check_messages()
        self.events = list(self.newEvents)
        self.newEvents = []
        return True

    def sendAll(self, data):
        for id, client in list(self.clients.items()):
            self.send(id, data)

    def sendAllExcept(self, id, data):
        for i, client in list(self.clients.items()):
            if i == id:
                continue
            self.send(i, data)

    def send(self, client, data):
        try:
            self.clients[client].socket.sendall(bytearray(data, "latin1"))
        except KeyError:
            pass
        except socket.error:
            self.disconnected(client)

    def get_new_clients(self):
        return [i[1] for i in self.events if i[0] == self._EVENT_NEW_CLIENT]

    def get_disconnected_clients(self):
        return [i[1] for i in self.events if i[0] == self._EVENT_CLIENT_DISCONNECTED]

    def get_messages(self):
        return [(i[1], i[2]) for i in self.events if i[0] == self._EVENT_MESSAGE]

    def _check_new_connections(self):
        rlist, wlist, xlist = select.select([self.listenSocket], [], [], 0)
        if self.listenSocket not in rlist:
            return
        joinedSocket, addr = self.listenSocket.accept()
        joinedSocket.setblocking(False)
        self.clients[self.nextId] = TelnetServer.Client(joinedSocket, addr[0])
        self.newEvents.append((self._EVENT_NEW_CLIENT, self.nextId))
        self.nextId += 1

    def _check_disconnected(self):
        for id, client in list(self.clients.items()):
            if time.time() - client.lastCheck < 5.0:
                continue
            self.send(id, "\x00")
            client.lastCheck = time.time()

    def _check_messages(self):
        for id, client in list(self.clients.items()):
            rlist, wlist, xlist = select.select([client.socket], [], [], 0)
            if client.socket not in rlist:
                continue
            try:
                data = client.socket.recv(4096).decode("latin1")
                message = self.cleanup(client, data)
                if message:
                    message = message.strip()
                    self.newEvents.append((self._EVENT_MESSAGE, id, message))
            except socket.error:
                self.disconnected(id)

    def disconnected(self, client):
        del(self.clients[client])
        self.newEvents.append((self._EVENT_CLIENT_DISCONNECTED, client))

    def cleanup(self, client, data):
        _READ_STATE_NORMAL = 1
        _READ_STATE_COMMAND = 2
        _READ_STATE_SUBNEG = 3
        message = None
        state = _READ_STATE_NORMAL
        for c in data:
            if state == _READ_STATE_NORMAL:
                if ord(c) == self._TN_INTERPRET_AS_COMMAND:
                    state = _READ_STATE_COMMAND
                elif c == "\n":
                    message = str(client.buffer)
                    client.buffer = ""
                elif c == "\x08":
                    client.buffer = client.buffer[:-1]
                else:
                    client.buffer += c
            elif state == _READ_STATE_COMMAND:
                if ord(c) == self._TN_SUBNEGOTIATION_START:
                    state = _READ_STATE_SUBNEG
                elif ord(c) in (self._TN_WILL, self._TN_WONT, self._TN_DO, self._TN_DONT):
                    state = _READ_STATE_SUBNEG
                else:
                    state = _READ_STATE_NORMAL
            elif state == _READ_STATE_SUBNEG:
                if ord(c) == self._TN_SUBNEGOTIATION_END:
                    state = _READ_STATE_NORMAL
        return message
