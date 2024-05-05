import sys

from package.engine.Evaluator import Evaluator
from package.lexical_analyser.LexicalAnalyser import LexicalAnalyser
from package.parser.Parser import Parser

no_of_args = len(sys.argv)

filename = sys.argv[1]

if no_of_args == 2:
    Evaluator.evaluate(filename)

else:
    if sys.argv[2] == "-ast":
        scanner = LexicalAnalyser(filename)

        tokens = scanner.scan()

        parser = Parser(tokens)
        AST = parser.parse()

        stringAST = parser.AstToString()

        for string in stringAST:
            print(string)

    else:
        print("Unknown flag:", sys.argv[2])
