from package.symbols.E import E
from package.symbols.B import B
from package.symbols.Beta import Beta
from package.symbols.Bool import Bool
from package.symbols.BOp import BOp
from package.symbols.Delta import Delta
from package.symbols.Dummy import Dummy
from package.symbols.Err import Err
from package.symbols.Eta import Eta
from package.symbols.Gamma import Gamma
from package.symbols.Id import Id
from package.symbols.Int import Int
from package.symbols.Lambda import Lambda
from package.symbols.Rand import Rand
from package.symbols.Rator import Rator
from package.symbols.Str import Str
from package.symbols.Symbol import Symbol
from package.symbols.Tau import Tau
from package.symbols.Tup import Tup
from package.symbols.UOp import UOp
from package.symbols.YStar import YStar


class CSEMachineFactory:
    def __init__(self) -> None:
        self.e0 = E(0)
        self.i = 1
        self.j = 0

    def getSymbol(self, node):
        match node.data:
            case "neg":
                return UOp(node.data)

            case "aug":
                return BOp(node.data)

            case "gamma":
                return Gamma()

            case "tau":
                return Tau(len(node.children))

            case "<Y*>":
                return YStar

            case _:
                if node.data.startsWith("<ID:"):
                    return Id(node.data[4:len(node.data)-1])
                elif node.data.startsWith("<INT:"):
                    return Int(node.data[5:len(node.data)-1])
                elif node.data.startsWith("<STR:"):
                    return Str(node.data[6:len(node.data)-2])
                elif node.data.startsWith("<nil>"):
                    return Tup()
                elif node.data.startsWith("<true>"):
                    return Bool("true")
                elif node.data.startsWith("<false>"):
                    return Bool("false")
                elif node.data.startsWith("<dummy>"):
                    return Dummy()
                else:
                    return Err(f"No symbol found for give node: {node.data}")

    def getB(self, node):
        b = B()
        b.symbols = self.getPreOrderTraversal(node)

        return b

    def getDelta(self, node):
        delta = Delta(self.j)
        self.j += 1
        delta.symbols = self.getPreOrderTraversal(node)

        return delta

    def getLambda(self, node):
        lambda_ = Lambda(self.i)
        self.i += 1
        lambda_.delta = self.getDelta(node.children[1])

        if node.children[0].data == ",":
            for identifier in node.children[0].children:
                lambda_.identifiers.append(
                    Id(identifier.data[4:len(identifier.data)-1]))
        else:
            bounded_var = node.children[0]
            lambda_.identifiers.append(
                Id(bounded_var.data[4:len(bounded_var.data)-1]))

        return lambda_

    def getPreOrderTraversal(self, node):
        symbols = []
        if node.data == "lambda":
            symbols.append(self.getLambda(node))

        elif node.data == "->":
            symbols.append(self.getDelta(node.children[1]))  # delta then
            symbols.append(self.getDelta(node.children[2]))  # delta else
            symbols.append(Beta())
            symbols.append(self.getB(node.children[0]))

        else:
            symbols.append(self.getSymbol(node))
            for child in node.children:
                symbols.extend(self.getPreOrderTraversal(child))

        return symbols

    def getControl(self, ast):
        control = []
        control.append(self.e0)
        control.append(self.getDelta(ast.root))

        return control

    def getStack(self):
        stack = []
        stack.append(self.e0)

        return stack

    def getEnv(self):
        return [self.e0]

    def getCSEMachine(self, ast):
        return CSEMachine(self.getControl(ast), self.getStack(), self.getEnv())


class CSEMachine:
    def __init__(self, control, stack, env) -> None:
        self.control = control
        self.stack = stack
        self.env = env

    def execute(self):
        currEnv = self.env[0]
        j = 1

        while self.control:
            # Pop the control
            currentSymbol = self.control.pop()

            # CSE Rule 1
            if isinstance(currentSymbol, Id):
                Ob = currEnv.lookup(currentSymbol)
                self.stack.append(Ob)

            # CSE Rule 2
            elif isinstance(currentSymbol, Lambda):
                lambda_ = currentSymbol
                lambda_.enviroment = currEnv.index
                self.stack.insert(0, lambda_)

            elif isinstance(currentSymbol, Gamma):
                # Get stack-top
                stackTop = self.stack.pop(0)
                # CSE Rule 4
                if isinstance(stackTop, Lambda):
                    lambda_ = stackTop
                    e = E(j)
                    j += 1

                    if (len(lambda_.identifiers) == 1):
                        e.values[lambda_.identifiers[0]] = self.stack.pop(0)

                    # CSE Rule 11
                    else:
                        tup = self.stack.pop(0)

                        i = 0
                        for id in lambda_.identifiers:
                            e.values[id] = tup.symbols[i]
                            i += 1

                    for env in self.env:
                        if env.index == lambda_.enviroment:
                            e.parent = env

                    currEnv = e
                    self.control.append(currEnv)
                    self.control.append(lambda_.delta)
                    self.stack.insert(0, currEnv)
                    self.env.append(currEnv)

                # CSE Rule 10
                elif isinstance(stackTop, Tup):
                    tup = stackTop
                    index = int(self.stack.pop(0))

                    # "index - 1" because Python lists are zero-indexed but RPAL lists are 1-indexed
                    tupleValue = stackTop.symbols[index-1]
                    self.stack.insert(0, tupleValue)

                # CSE Rule 12
                elif isinstance(stackTop, YStar):
                    lambda_ = self.stack.pop(0)
                    eta = Eta()
                    eta.index = lambda_.index
                    eta.environment = lambda_.environment
                    eta.identifier = lambda_.identifiers[0]
                    eta.lambda_ = lambda_

                    self.stack.insert(0, eta)

                # CSE Rule 13
                elif isinstance(stackTop, Eta):
                    eta = stackTop
                    self.control.append(Gamma())
                    self.control.append(Gamma())

                    lambda_ = eta.lambda_

                    self.stack.insert(0, eta)
                    self.stack.insert(0, lambda_)

                # Built-in functions
                else:
                    pass

            # CSE Rule 5
            elif isinstance(currentSymbol, E):
                value = self.stack.pop(0)
                env = self.stack.pop(0)

                self.stack.insert(0, value)

                self.env[currentSymbol.index].isRemoved = True

                y = len(self.env)

                # Traverse list of envs in reverse order to find the new current env
                while y > 0:
                    if not self.env[y-1].isRemoved:
                        currEnv = self.enc[y-1]
                        break
                    y -= 1

            elif isinstance(currentSymbol, Rator):
                rator = currentSymbol
                # CSE Rule 6
                if isinstance(currentSymbol, BOp):
                    rand1 = self.stack.pop(0)
                    rand2 = self.stack.pop(0)

                    result = self.applyBOp(rator, rand1, rand2)

                # CSE Rule 7
                elif isinstance(currentSymbol, UOp):
                    rand = self.stack.pop(0)

                    result = self.applyUOp(rator, rand)

                self.stack.insert(0, result)

            # CSE Rule 8
            elif isinstance(currentSymbol, Beta):
                boolOnStack = self.stack.pop(0)
                del_else = self.control.pop()
                del_then = self.control.pop()

                if (bool(boolOnStack.data)):
                    self.control.append(del_then)

                else:
                    self.control.append(del_else)

            # CSE Rule 9
            elif isinstance(currentSymbol, Tau):
                tup = Tup()
                for _ in range(currentSymbol.n):
                    tup.symbols.append(self.stack.pop(0))

                self.stack.insert(0, tup)

            # DELTA

    def applyUOp(self, rator, rand):
        if rator.data == "neg":
            return Int(str(-1 * int(rand.data)))

        elif rator.data == "not":
            return str(not bool(rand.data))

        else:
            return Err("Unknown unary operator encountered!")

    def applyBOp(self, rator, rand1, rand2):
        if rator.data == "+":
            return Int(str(int(rand1.data) + int(rand2.data)))

        elif rator.data == "-":
            return Int(str(int(rand1.data) - int(rand2.data)))

        elif rator.data == "*":
            return Int(str(int(rand1.data) * int(rand2.data)))

        elif rator.data == "/":
            return Int(str(int(rand1.data) / int(rand2.data)))

        elif rator.data == "**":
            return Int(str(int(rand1.data) ** int(rand2.data)))

        elif rator.data == "&":
            return Bool(str(bool(rand1.data) and bool(rand2.data)))

        elif rator.data == "or":
            return Bool(str(bool(rand1.data) or bool(rand2.data)))

        elif rator.data == "eq":
            return Bool(str(rand1.data == rand2.data))

        elif rator.data == "ne":
            return Bool(str(rand1.data != rand2.data))

        elif rator.data == "ls":
            return Bool(str(int(rand1.data) < int(rand2.data)))

        elif rator.data == "le":
            return Bool(str(int(rand1.data) <= int(rand2.data)))

        elif rator.data == "gr":
            return Bool(str(int(rand1.data) > int(rand2.data)))

        elif rator.data == "ge":
            return Bool(str(int(rand1.data) >= int(rand2.data)))

        elif rator.data == "aug":
            if not isinstance(rand1, Tup):
                return Err("'aug' operator expects a tuple or nil")

            if isinstance(rand2, Tup):
                rand1.symbols.extend(rand2.symbols)
            else:
                rand1.symbols.append(rand2)

            return rand1

        else:
            return Err("Unknown binary operator encountered!")
