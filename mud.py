import xml.etree.ElementTree as etree

class   Mud():
    class   Room():
        class   Exit():
            def __init__(self, name, direction, to):
                self.name = name
                self.direction = direction
                self.to = to

            def __str__(self):
                return self.direction + "(" + self.name + ")"

        def __init__(self, name, desc, exits):
            self.name = name
            self.desc = desc
            self.exits = [Mud.Room.Exit(*i) for i in exits]

    class   Npc():
        class   Dialog():
            def __init__(self, tag, text, condition):
                self.condition = condition
                self.tag = tag
                self.text = text.split(' ')
            
            def __str__(self):
                return self.tag + " : " + self.condition + " => " + ' '.join(self.text)

            def checkCondition(self, message, player):
                if len(message) < 1:
                    return
                if message[0] == self.tag and self.condition in message:
                    m = []
                    for i in self.text:
                        if i[:1] == "${" and i[-1] == "}":
                            m.append(eval(i[2:-1]))
                        else:
                            m.append(i)
                    return ' '.join(m)

        def __init__(self, room, name, description, text):
            self.name = name
            self.desc = description
            self.text = [Mud.Npc.Dialog(*i) for i in text]
            self.room = room

        def checkSpeech(self, message, player):
            ret = []
            for i in self.text:
                a = i.checkCondition(message, player)
                if a:
                    ret.append(a)
            return ret
        
        def __str__(self):
            return self.name

    def __init__(self, file):
        tree = etree.parse(file)
        root = tree.getroot()
        self.rooms = {}
        self.npcs = {}
        self.begin = None
        for child in root:
            if child.tag == "room":
                self.room(child)
            elif child.tag == "npc":
                self.npc(child)
        
    def npc(self, child):
        dialog = []
        name = None
        room = child.attrib["room"]
        desc = None
        for i in range(len(child)):
            if child[i].tag == "name":
                name = child[i].text
            elif child[i].tag == "description":
                desc = child[i].text
            elif child[i].tag == "dialog":
                for j in child[i]:
                    dialog.append((j.tag, j.text, j.attrib["condition"]))
        if not name or not desc or not room:
            return
        self.npcs[name] = Mud.Npc(room, name, desc, dialog)

    def room(self, child):
        exits = []
        name = None
        desc = None
        for i in range(len(child)):
            if child[i].tag == "name":
                name = child[i].text
            elif child[i].tag == "description":
                desc = child[i].text
            elif child[i].tag == "exit":
                exits.append((child[i].text, child[i].attrib["direction"],
                    child[i].attrib["to"]))
        if not name or not desc:
            return
        self.rooms[name] = Mud.Room(name, desc, exits)
        try:
            if child.attrib['attribute'] == "begin":
                self.begin = self.rooms[child[0].text]
        except KeyError:
            pass

    def getNpcsInRoom(self, room):
        ret = []
        for j, i in self.npcs.items():
            if i.room == room.name:
                ret.append(i)
        return ret

    def print_rooms(self):
        for j, i in self.rooms.items():
            print(i.name)
            print(i.desc)
            print(*i.exits)

    def print_npcs(self):
        for j, i in self.npcs.items():
            print(i.name)
            print(i.desc)
            print(*i.text)
