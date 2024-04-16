from Symbol import Symbol


class Delta(Symbol):
    def __init__(self, i) -> None:
        super().__init__("delta")
        self.index = i
