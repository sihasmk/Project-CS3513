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
        Evaluator.evaluate(filename, True)

    else:
        print("Unknown flag:", sys.argv[2])
