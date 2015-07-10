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
            self.exits = [Mud.Room.Exit(i[0], i[1], i[2]) for i in exits]

    class   Npc():
        class   Dialog():
            def __init__(self, condition, text):
                self.condition = condition
                self.text = text
            
            def __str__(self):
                return self.condition + " => " + self.text

        def __init__(self, name, description, text):
            self.name = name
            self.desc = description
            self.text = [Mud.Npc.Dialog(i[0], i[1]) for i in text]

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
        desc = None
        for i in range(len(child)):
            if child[i].tag == "name":
                name = child[i].text
            elif child[i].tag == "description":
                desc = child[i].text
            elif child[i].tag == "text":
                dialog.append((child[i].text, child[i].attrib["condition"]))
        if not name or not desc:
            return
        self.npcs[name] = Mud.Npc(name, desc, dialog)

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

    def print_rooms(self):
        for j, i in self.rooms.items():
            print(i.name)
            print(i.desc)
            print(i.exits)

    def print_npcs(self):
        for j, i in self.npcs.items():
            print(i.name)
            print(i.desc)
            print(i.text)
