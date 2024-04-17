from collections import deque

from package.engine.NodeAndNodeFactory import NodeFactory
from package.parser.NodeType import NodeType


class ASTFactory:
    def __init__(self) -> None:
        pass

    @staticmethod
    # A function that takes in the string AST, and returns the root of the AST
    # Each node in the AST will have a parent attribute as well as a list containing all its children
    def getAST(data):
        root = NodeFactory.getNode(data[0], 0)
        prevNode = root
        depth = 0

        for string in data[1:]:
            d = 0

            while string[d] == '.':
                d += 1

            currNode = NodeFactory.getNode(string[d:], d)

            if depth < d:
                prevNode.children.append(currNode)
                currNode.parent = prevNode

            else:
                while prevNode.depth != d:
                    prevNode = prevNode.parent

                prevNode.parent.children.append(currNode)
                currNode.parent = prevNode.parent

            prevNode = currNode
            depth = d

        return AST(root)


class AST:
    def __init__(self, root) -> None:
        self.root = root

    def standardize(self):
        if not self.root.isStandardized:
            self.root.standardize()

    def preOrderTraverse(self, node, i):
        for _ in range(i):
            print(".", end="")

        print(node.data)

        for child in node.children:
            self.preOrderTraverse(child, i+1)
