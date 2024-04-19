from package.symbols.Symbol import Symbol


class Lambda(Symbol):
    def __init__(self, i) -> None:
        super().__init__("lambda")
        self.index = i
        self.environment = 0
        self.identifiers = []
        self.delta = None
