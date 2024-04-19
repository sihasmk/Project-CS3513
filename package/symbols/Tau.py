from package.symbols.Symbol import Symbol


class Tau(Symbol):
    def __init__(self, n) -> None:
        super().__init__("tau")
        self.n = n
