from NodeType import NodeType


class Node:
    def __init__(self, type, value, children) -> None:
        self.type = type
        self.value = value
        self.children = children

# We consider the root node to have a depth of 0
