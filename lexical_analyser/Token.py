class Token:
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __str__(self) -> str:
        if self.value == "\n":
            return "<{},{}>".format(self.type, "'\\n'")

        return "<{},'{}'>".format(self.type, self.value)
