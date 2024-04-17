from package.lexical_analyser.LexicalAnalyser import LexicalAnalyser
from package.parser.Parser import Parser
from package.engine.ASTAndASTFactory import ASTFactory

scanner = LexicalAnalyser("input_file.txt")
tokens = scanner.scan()

for token in tokens:
    print(token)

parser = Parser(tokens)
AST = parser.parse()

for node in AST:
    print(node)

stringAST = parser.AstToString()

AST = ASTFactory.getAST(stringAST)

for string in stringAST:
    print(string)
