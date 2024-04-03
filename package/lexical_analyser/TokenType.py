from enum import Enum, auto


class TokenType(Enum):
    KEYWORD = auto()
    IDENTIFIER = auto()
    INTEGER = auto()
    OPERATOR = auto()
    STRING = auto()
    PUNCTUATION = auto()
    DELETE = auto()
    ENDOFTOKENS = auto()

    def __str__(self) -> str:
        return self.name
