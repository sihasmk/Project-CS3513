from package.symbols.Symbol import Symbol


class B(Symbol):
    def __init__(self) -> None:
        self.symbols = []
        super().__init__("b")
