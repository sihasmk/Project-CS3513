from package.lexical_analyser.LexicalAnalyser import LexicalAnalyser
from package.parser.Parser import Parser
from package.engine.ASTAndASTFactory import ASTFactory
from package.engine.CSEMachineAndCSEMachineFactory import CSEMachineFactory, CSEMachine


class Evaluator:
    @staticmethod
    def evaluate(filename):
        scanner = LexicalAnalyser(filename)

        tokens = scanner.scan()

        parser = Parser(tokens)
        AST = parser.parse()

        stringAST = parser.AstToString()

        ast = ASTFactory.getAST(stringAST)

        ast.standardize()

        cseMachineFact = CSEMachineFactory()

        cseMachine = cseMachineFact.getCSEMachine(ast)

        return cseMachine.getResult()
