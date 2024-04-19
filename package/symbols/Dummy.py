from package.symbols.Rand import Rand


class Dummy(Rand):
    def __init__(self) -> None:
        super().__init__("dummy")
