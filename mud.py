import xml.etree.ElementTree as etree

class   Mud():
    class   Room():
        def __init__(self, name, desc, exits):
            self.name = name
            self.desc = desc
            self.exits = exits

    def __init__(self, file):
        tree = etree.parse(file)
        root = tree.getroot()
        self.rooms = []
        for child in root:
            if child.tag not in "room":
                continue
            exits = []
            for j in range(2, len(child)):
                exits.append(child[j].text)
            self.rooms.append(Mud.Room(child[0].text, child[1].text, exits))

    def print_rooms(self):
        for i in self.rooms:
            print(i.name)
            print(i.desc)
            print(i.exits)
