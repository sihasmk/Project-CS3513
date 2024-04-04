from pathlib import Path
import re
from .Token import Token
from .TokenType import TokenType


class LexicalAnalyser:
    def __init__(self, inputFileName):
        self.inputFileName = inputFileName
        self.tokens = []

    def scan(self):
        try:
            p = Path(__file__).parent.parent / self.inputFileName
            input_file = open(p, 'r')
            count = 0
            while True:
                count += 1
                line = input_file.readline()

                if not line:
                    break

                self.tokenizeLine(line)

            input_file.close()

        except IOError:
            print("Could not read file {}".format(self.inputFileName))

        filtered_tokens = [
            token for token in self.tokens if token.type != TokenType.DELETE]

        return filtered_tokens

    def tokenizeLine(self, line):
        digit = r"[0-9]"
        letter = r"[a-zA-Z]"
        operatorSymbol = r"[+\-*<>&.@/:=~|$!#%^_\[\]{}\"`?]"
        punction = r"[();,]"

        identifierPattern = re.compile(
            letter+r"("+letter+r"|"+digit+r"|"+r"_)*")
        integerPattern = re.compile(digit+r"+")
        operatorPattern = re.compile(operatorSymbol+r"+")

        stringPattern = re.compile(
            r'''"(\t|\n|\\|\"|'''+punction+'''| |'''+letter+'''|'''+digit+'''|'''+operatorSymbol+''')*"''')
        commentPattern = re.compile(r"//.*")
        spacesPattern = re.compile(r"[ \t\n]+")
        punctuationPattern = re.compile(punction)

        currentIndex = 0

        while (currentIndex < len(line)):
            currentChar = line[currentIndex]

            spaceMatch = re.match(spacesPattern, line[currentIndex:])
            commentMatch = re.match(commentPattern, line[currentIndex:])

            if commentMatch:
                comment = commentMatch.group()
                self.tokens.append(Token(TokenType.DELETE, comment))
                currentIndex += len(comment)
                continue

            if spaceMatch:
                space = spaceMatch.group()
                self.tokens.append(Token(TokenType.DELETE, space))
                currentIndex += len(space)
                continue

            match = re.match(identifierPattern, line[currentIndex:])
            if match:
                identifier = match.group()

                keywords = ["let", "in", "fn", "where", "aug", "or", "not", "gr", "ge", "ls",
                            "le", "eq", "ne", "true", "false", "nil", "dummy", "within", "and", "rec"]

                if identifier in keywords:
                    self.tokens.append(Token(TokenType.KEYWORD, identifier))
                else:
                    self.tokens.append(Token(TokenType.IDENTIFIER, identifier))

                currentIndex += len(identifier)
                continue

            match = re.match(integerPattern, line[currentIndex:])
            if match:
                integer = match.group()
                self.tokens.append(Token(TokenType.INTEGER, integer))
                currentIndex += len(integer)
                continue

            match = re.match(stringPattern, line[currentIndex:])
            if match:
                string = match.group()
                self.tokens.append(Token(TokenType.STRING, string))
                currentIndex += len(string)
                continue

            match = re.match(operatorPattern, line[currentIndex:])
            if match:
                operator = match.group()
                self.tokens.append(Token(TokenType.OPERATOR, operator))
                currentIndex += len(operator)
                continue

            match = re.fullmatch(punctuationPattern, currentChar)
            if match:
                self.tokens.append(Token(TokenType.PUNCTUATION, currentChar))
                currentIndex += 1
                continue

            print("Unable to tokenize the character: {} at index: {}".format(
                currentChar, currentIndex))
            break
