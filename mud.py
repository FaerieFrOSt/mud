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

    def __init__(self, file):
        tree = etree.parse(file)
        root = tree.getroot()
        self.rooms = {}
        self.begin = None
        for child in root:
            if child.tag != "room":
                continue
            exits = []
            for j in range(2, len(child)):
                exits.append((child[j].text, child[j].attrib["direction"],
                    child[j].attrib["to"]))
            self.rooms[child[0].text] = Mud.Room(child[0].text, child[1].text, exits)
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
