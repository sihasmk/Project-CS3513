from Symbol import Symbol
from E import E
from Id import Id


class E(Symbol):
    def __init__(self, i) -> None:
        super().__init__("e")
        self.index = i
        self.parent = None
        self.isRemoved = False
        self.values = {}

    def lookup(self, id) -> Symbol:
        for key in self.values.keys:
            if key.data == id.data:
                return self.values.get(key)

        if self.parent:
            return self.parent.lookup(id)

        else:
            return Symbol(id.data)
