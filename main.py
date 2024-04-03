from package.lexical_analyser.LexicalAnalyser import LexicalAnalyser
from package.parser.Parser import Parser

scanner = LexicalAnalyser("input_file.txt")
tokens = scanner.scan()
parser = Parser(tokens)
AST = parser.parse()

for node in AST:
    print(node)
