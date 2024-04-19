from package.symbols.Symbol import Symbol


class Err(Symbol):
    def __init__(self, message="") -> None:
        if message:
            print("Error: ", end="")
            print(message)
        super().__init__("error")
