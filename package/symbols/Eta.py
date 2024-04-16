from Symbol import Symbol


class Eta(Symbol):
    def __init__(self) -> None:
        super().__init__("eta")
        self.index = 0
        self.environment = 0
        self.identifier = None
        self.lambda_ = None  # Since lambda is reserved in Python
