from package.lexical_analyser.LexicalAnalyser import LexicalAnalyser
from package.parser.Parser import Parser

scanner = LexicalAnalyser("input_file.txt")
tokens = scanner.scan()
parser = Parser(tokens)
AST = parser.parse()

stringAST = parser.AstToString()

for string in stringAST:
    print(string)
