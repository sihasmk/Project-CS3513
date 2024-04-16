from Node import Node


class NodeFactory:
    def __init__(self) -> None:
        pass

    @staticmethod
    def getNode(*args):
        node = Node()
        node.data = args[0]
        node.depth = args[1]

        if len(args) > 2:
            node.parent = args[2]
            node.children = args[3]
            node.isStandardized = args[4]

        node.children = []

        return node
