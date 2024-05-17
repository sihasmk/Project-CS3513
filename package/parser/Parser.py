import sys
from ..lexical_analyser.Token import Token
from ..lexical_analyser.TokenType import TokenType
from .NodeType import NodeType
from .Node import Node


class Parser:
    def __init__(self, tokens) -> None:
        self.tokens = tokens
        self.AST = []
        self.stringAST = []

    # Function with the logic to convert AST to a list of strings to show their depth
    # Depth is found here and the addString function uses the dots given from here to add to stringAST
    def AstToString(self):
        dots = ""
        stack = []

        while self.AST:
            if not stack:
                if self.AST[-1].children == 0:
                    self.addStrings(dots, self.AST.pop())

                else:
                    node = self.AST.pop()
                    stack.append(node)

            else:
                if self.AST[-1].children > 0:
                    node = self.AST.pop()
                    stack.append(node)
                    dots += "."

                else:
                    stack.append(self.AST.pop())
                    dots += "."

                    while (stack[-1].children == 0):
                        self.addStrings(dots, stack.pop())

                        if not stack:
                            break

                        dots = dots[:-1]
                        node = stack.pop()
                        node.children -= 1
                        stack.append(node)

        self.stringAST.reverse()
        return self.stringAST

    # Function to prepend the dots to a node, and add it to stringAST list
    def addStrings(self, dots, node):
        match node.type:
            case NodeType.identifier:
                self.stringAST.append(dots+"<ID:"+node.value+">")
            case NodeType.integer:
                self.stringAST.append(dots+"<INT:"+node.value+">")
            case NodeType.string:
                self.stringAST.append(dots+"<STR:"+node.value+">")
            case NodeType.true_value, NodeType.false_value, NodeType.nil, NodeType.dummy:
                self.stringAST.append(dots+"<"+node.value+">")
            case NodeType.fcn_form:
                self.stringAST.append(dots+"function_form")
            case _:
                self.stringAST.append(dots+node.value)

    def parse(self):
        # To know when we have gotten the last token
        self.tokens.append(Token(TokenType.ENDOFTOKENS, ""))
        self.E()

        if (self.tokens[0].type == TokenType.ENDOFTOKENS):
            return self.AST

        else:
            print("Parsing unsuccessful...")
            print("Remaining unparsed tokens:")
            for token in self.tokens:
                print(token)
            return None

    def E(self):
        n = 0
        token = self.tokens[0]

        if token.type == TokenType.KEYWORD and token.value in ["let", "fn"]:
            if token.value == "let":
                self.tokens.pop(0)
                self.D()

                if (self.tokens[0].value != "in"):
                    print("Parse error at E : 'in' expected")
                    sys.exit()

                self.tokens.pop(0)
                self.E()
                self.AST.append(Node(NodeType.let, "let", 2))

            else:
                self.tokens.pop(0)

                while True:
                    self.Vb()
                    n += 1

                    if ((self.tokens[0].type != TokenType.IDENTIFIER) and (self.tokens[0].value != "(")):
                        break

                if not self.tokens[0].value == ".":
                    print("Parse error at E : '.' expected")
                    sys.exit()

                self.tokens.pop(0)
                self.E()
                self.AST.append(Node(NodeType.lambda_, "lambda", n+1))

        else:
            self.Ew()

    def Ew(self):
        self.T()
        if (self.tokens[0].value == "where"):
            self.tokens.pop(0)  # remove the "where"
            self.Dr()
            self.AST.append(Node(NodeType.where, "where", 2))

    def T(self):
        self.Ta()
        n = 1

        while (self.tokens[0].value == ","):
            self.tokens.pop(0)  # remove commas
            self.Ta()
            n += 1

        if (n > 1):
            self.AST.append(Node(NodeType.tau, "tau", n))

    def Ta(self):
        self.Tc()
        while (self.tokens[0].value == "aug"):
            self.tokens.pop(0)
            self.Tc()
            self.AST.append(Node(NodeType.aug, "aug", 2))

    def Tc(self):
        self.B()
        if (self.tokens[0].value == "->"):
            self.tokens.pop(0)  # Remove the '->'
            self.Tc()

            if not self.tokens[0].value == "|":
                print("Parse error at Tc: conditional '|' expected")
                sys.exit()

            self.tokens.pop(0)
            self.Tc()
            self.AST.append(Node(NodeType.conditional, "->", 3))

    def B(self):
        self.Bt()

        while (self.tokens[0].value == "or"):
            self.tokens.pop(0)  # Remove the 'or'
            self.Bt()
            self.AST.append(Node(NodeType.op_or, "or", 2))

    def Bt(self):
        self.Bs()

        while (self.tokens[0].value == "&"):
            self.tokens.pop(0)  # Remove the '&'
            self.Bs()
            self.AST.append(Node(NodeType.op_and, "&", 2))

    def Bs(self):
        if (self.tokens[0].value == "not"):
            self.tokens.pop(0)
            self.Bp()
            self.AST.append(Node(NodeType.op_not, "not", 1))

        else:
            self.Bp()

    def Bp(self):
        self.A()
        token = self.tokens[0]

        if token.value in [">", ">=", "<", "<=", "gr", "ge", "ls", "le", "eq", "ne"]:
            self.tokens.pop(0)
            self.A()

            match token.value:
                case ">":
                    self.AST.append(Node(NodeType.op_compare, "gr", 2))
                case ">=":
                    self.AST.append(Node(NodeType.op_compare, "ge", 2))
                case "<":
                    self.AST.append(Node(NodeType.op_compare, "ls", 2))
                case ">=":
                    self.AST.append(Node(NodeType.op_compare, "le", 2))
                case _:
                    self.AST.append(Node(NodeType.op_compare, token.value, 2))

    def A(self):
        if self.tokens[0].value == "+":
            self.tokens.pop(0)
            self.At()

        elif self.tokens[0].value == "-":
            self.tokens.pop(0)
            self.At()
            self.AST.append(Node(NodeType.op_neg, "neg", 1))

        else:
            self.At()

        while self.tokens[0].value in ["+", "-"]:
            currTok = self.tokens[0]
            self.tokens.pop(0)  # Remove the + or - symbols
            self.At()
            if currTok.value == "+":
                self.AST.append(Node(NodeType.op_plus, "+", 2))
            else:
                self.AST.append(Node(NodeType.op_minus, "-", 2))

    def At(self):
        self.Af()
        while (self.tokens[0].value in ["*", "/"]):
            currTok = self.tokens[0]
            self.tokens.pop(0)  # Remove the multiply or divide operator
            self.Af()

            if (currTok.value == "*"):
                self.AST.append(Node(NodeType.op_mul, "*", 2))

            else:
                self.AST.append(Node(NodeType.op_div, "/", 2))

    def Af(self):
        self.Ap()

        if (self.tokens[0].value == "**"):
            self.tokens.pop(0)
            self.Af()
            self.AST.append(Node(NodeType.op_pow, "**", 2))

    def Ap(self):
        self.R()

        while self.tokens[0].value == "@":
            self.tokens.pop(0)

            if self.tokens[0].type != TokenType.IDENTIFIER:
                print("Parsing error at Ap: IDENTIFIER expected")
                sys.exit()

            self.AST.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            self.tokens.pop(0)  # Remove IDENTIFIER

            self.R()
            self.AST.append(Node(NodeType.at, "@", 3))

    def R(self):
        self.Rn()

        while (self.tokens[0].type in [TokenType.IDENTIFIER, TokenType.INTEGER, TokenType.STRING]) or (self.tokens[0].value in ["true", "false", "dummy", "nil", "("]):
            self.Rn()
            self.AST.append(Node(NodeType.gamma, "gamma", 2))

    def Rn(self):
        match self.tokens[0].type:
            case TokenType.IDENTIFIER:
                self.AST.append(
                    Node(NodeType.identifier, self.tokens[0].value, 0))
                self.tokens.pop(0)
            case TokenType.INTEGER:
                self.AST.append(
                    Node(NodeType.integer, self.tokens[0].value, 0))
                self.tokens.pop(0)
            case TokenType.STRING:
                self.AST.append(Node(NodeType.string, self.tokens[0].value, 0))
                self.tokens.pop(0)
            case TokenType.KEYWORD:
                match self.tokens[0].value:
                    case "true":
                        self.AST.append(Node(NodeType.true_value, "true", 0))
                        self.tokens.pop(0)
                    case "false":
                        self.AST.append(Node(NodeType.false_value, "false", 0))
                        self.tokens.pop(0)
                    case "nil":
                        self.AST.append(Node(NodeType.nil, "nil", 0))
                        self.tokens.pop(0)
                    case "dummy":
                        self.AST.append(Node(NodeType.dummy, "dummy", 0))
                        self.tokens.pop(0)
                    case _:
                        print("Parse error at Rn: Unexpected keyword")
                        sys.exit()

            case TokenType.PUNCTUATION:
                if self.tokens[0].value == "(":
                    self.tokens.pop(0)  # Remove the opening bracket
                    self.E()

                    if (self.tokens[0].value != ")"):
                        print("Parsing error at Rn : Expected a matching ')'")
                        sys.exit()

                    self.tokens.pop(0)  # Remove closing bracket
            case _:
                print("Parsing error at Rn: Expected an Rn, but got something else")
                sys.exit()

    def D(self):
        self.Da()
        if (self.tokens[0].value == "within"):
            self.tokens.pop(0)  # Remove 'within'
            self.D()
            self.AST.append(Node(NodeType.within, "within", 2))

    def Da(self):
        self.Dr()
        n = 1

        while self.tokens[0].value == "and":
            self.tokens.pop(0)  # Remove 'and's
            self.Dr()
            n += 1

        if (n > 1):
            self.AST.append(Node(NodeType.and_, "and", n))

    def Dr(self):
        isRec = False

        if self.tokens[0].value == "rec":
            self.tokens.pop(0)  # Remove 'rec' word
            isRec = True

        self.Db()

        if isRec:
            self.AST.append(Node(NodeType.rec, "rec", 1))

    def Db(self):
        if (self.tokens[0].type == TokenType.PUNCTUATION) and (self.tokens[0].value == "("):
            self.tokens.pop(0)  # Remove the opening bracket
            self.D()

            if self.tokens[0].value != ")":
                print("Parsing error at Db: Expected matching ')'")
                sys.exit()

            self.tokens.pop(0)

        elif self.tokens[0].type == TokenType.IDENTIFIER:
            # Hoping to get fcn_form
            if (self.tokens[1].value == "(") or (self.tokens[1].type == TokenType.IDENTIFIER):
                self.AST.append(
                    Node(NodeType.identifier, self.tokens[0].value, 0))

                self.tokens.pop(0)  # Remove the ID

                n = 1

                while True:
                    self.Vb()
                    n += 1

                    if (self.tokens[0].type != TokenType.IDENTIFIER and self.tokens[0].value != "("):
                        break

                if (self.tokens[0].value != "="):
                    print("Parsing error at Db : Expected an '='")
                    sys.exit()

                self.tokens.pop(0)
                self.E()

                self.AST.append(Node(NodeType.fcn_form, "fcn_form", n+1))

            elif self.tokens[1].value == "=":
                self.AST.append(
                    Node(NodeType.identifier, self.tokens[0].value, 0))
                self.tokens.pop(0)  # Remove ID
                self.tokens.pop(0)  # Remove '='
                self.E()

                self.AST.append(Node(NodeType.equal, "=", 2))

            elif self.tokens[1].value == ",":
                self.Vl()
                if (self.tokems[0] != "="):
                    print("Parsing error at Db : Expected an '='")
                    sys.exit()

                self.tokens.pop(0)
                self.E()

                self.AST.append(Node(NodeType.equal, "=", 2))

    def Vb(self):
        if self.tokens[0].type == TokenType.PUNCTUATION and self.tokens[0].value == "(":
            self.tokens.pop(0)  # Remove the opening bracket
            isVl = False

            if self.tokens[0].type == TokenType.IDENTIFIER:
                self.Vl()
                isVl = True

            if self.tokens[0].value != ")":
                print("Parse error at Vb : Unmatched '('")
                sys.exit()

            self.tokens.pop(0)

            if isVl:
                self.AST.append(
                    Node(NodeType.identifier, self.tokens[0].value, 0))
                self.tokens.pop(0)

            else:
                self.AST.append(Node(NodeType.empty_params, "()", 0))

        elif self.tokens[0].type == TokenType.IDENTIFIER:
            self.AST.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            self.tokens.pop(0)

    def Vl(self):
        n = 0

        while True:
            if n > 0:
                self.tokens.pop(0)

            if (self.tokens[0].type != TokenType.IDENTIFIER):
                print("Parse error at Vl : an ID was expected")
                sys.exit()

            self.AST.append(Node(NodeType.identifier, self.tokens[0].value, 0))
            self.tokens.pop(0)
            n += 1

            if (self.tokens[0].value != ","):
                break

        if n > 1:
            self.AST.append(Node(NodeType.comma, ",", n))
