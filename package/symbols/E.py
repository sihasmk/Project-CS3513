from package.symbols.Symbol import Symbol


class E(Symbol):
    def __init__(self, i) -> None:
        super().__init__("e")
        self.index = i
        self.parent = None
        self.isRemoved = False
        self.values = {}

    # Function to find the value of something in the env or parent envs
    def lookup(self, id) -> Symbol:
        for key in self.values:
            if key.data == id.data:
                return self.values[key]

        if self.parent is not None:
            return self.parent.lookup(id)

        else:
            return Symbol(id.data)
