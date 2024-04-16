from Symbol import Symbol


class Err(Symbol):
    def __init__(self) -> None:
        super().__init__("error")
