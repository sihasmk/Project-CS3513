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
from package.symbols.Rator import Rator
from package.symbols.Str import Str
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
            case "not" | "neg":
                return UOp(node.data)

            case "+" | "-" | "*" | "/" | "**" | "&" | "or" | "eq" | "ne" | "ls" | "le" | "gr" | "ge" | "aug":
                return BOp(node.data)

            case "gamma":
                return Gamma()

            case "tau":
                return Tau(len(node.children))

            case "<Y*>":
                return YStar()

            case _:
                if node.data.startswith("<ID:"):
                    return Id(node.data[4:len(node.data)-1])
                elif node.data.startswith("<INT:"):
                    return Int(node.data[5:len(node.data)-1])
                elif node.data.startswith("<STR:"):
                    return Str(node.data[6:len(node.data)-2])
                elif node.data.startswith("nil"):
                    return Tup()
                # Since we're using Python, we need to capitalize the boolean or else it will cause problems
                elif node.data.startswith("true"):
                    return Bool("True")
                elif node.data.startswith("false"):
                    return Bool("False")
                elif node.data.startswith("<dummy>"):
                    return Dummy()
                else:
                    return Err(f"No symbol found for given node: {node.data}")

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

    def printControl(self):
        for ele in self.control:
            print(ele.data, end=" ")

    def printStack(self):
        for ele in self.stack:
            print(ele.data, end=" ")

    def execute(self):
        currEnv = self.env[0]
        j = 1

        while self.control:
            # print("\nControl stack: ")
            # self.printControl()

            # print("\nData stack: ")
            # self.printStack()

            # Pop the control
            currentSymbol = self.control.pop()

            # CSE Rule 1
            if isinstance(currentSymbol, Id):
                Ob = currEnv.lookup(currentSymbol)
                self.stack.insert(0, Ob)

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
                    index = int(self.stack.pop(0).data)

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
                    builtInFunction = stackTop.data

                    match builtInFunction:
                        case "Print":
                            thingToBePrinted = self.stack.pop(0)
                            if not isinstance(thingToBePrinted, Tup):
                                print(thingToBePrinted.data)
                            else:
                                print(self.getStringTuple(thingToBePrinted))

                            self.stack.insert(0, Dummy())

                        case "Stem":
                            stringToBeStemmed = self.stack.pop(0)
                            # Not sure what 'Stem' does. Need to implement.

                        case "Stern":
                            stringToBeSterned: Str = self.stack.pop(0)

                            stringToBeSterned.data = stringToBeSterned.data[1:]
                            self.stack.insert(0, stringToBeSterned)

                        case "Conc":
                            str1 = self.stack.pop(0)
                            str2 = self.stack.pop(0)

                            str1.data += str2.data
                            self.stack.insert(0, str1)

                        case "Order":
                            tup: Tup = self.stack.pop(0)

                            size = len(tup.symbols)
                            self.stack.insert(0, Int(str(size)))

                        case "Null":
                            tup: Tup = self.stack.pop(0)
                            result = True

                            if tup.symbols:
                                result = False

                            self.stack.insert(0, Bool(str(result)))

                        case "Isinteger":
                            possibleInteger = self.stack.pop(0)

                            if isinstance(possibleInteger, Int):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

                        case "Isstring":
                            possibleString = self.stack.pop(0)

                            if isinstance(possibleString, Str):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

                        case "Istuple":
                            possibleTuple = self.stack.pop(0)

                            if isinstance(possibleTuple, Tup):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

                        case "Isdummy":
                            possibleDummy = self.stack.pop(0)

                            if isinstance(possibleDummy, Dummy):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

                        case "Istruthvalue":
                            possibleTruthvalue = self.stack.pop(0)

                            if isinstance(possibleTruthvalue, Bool):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

                        case "Isfunction":
                            possibleLambda = self.stack.pop(0)

                            if isinstance(possibleLambda, Lambda):
                                self.stack.insert(0, Bool("True"))
                            else:
                                self.stack.insert(0, Bool("False"))

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
                        currEnv = self.env[y-1]
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

                if (eval(boolOnStack.data)):
                    self.control.append(del_then)

                else:
                    self.control.append(del_else)

            # CSE Rule 9
            elif isinstance(currentSymbol, Tau):
                tup = Tup()
                for _ in range(currentSymbol.n):
                    tup.symbols.append(self.stack.pop(0))

                self.stack.insert(0, tup)

            # Encountering delta (delta-then or delta-else)
            elif isinstance(currentSymbol, Delta):
                self.control.extend(currentSymbol.symbols)

            elif isinstance(currentSymbol, B):
                self.control.extend(currentSymbol.symbols)

            # Int
            else:
                self.stack.insert(0, currentSymbol)

    def applyUOp(self, rator, rand):
        if rator.data == "neg":
            return Int(str(-1 * int(rand.data)))

        elif rator.data == "not":
            return Bool(str(not eval(rand.data)))

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
            return Bool(str(eval(rand1.data) and eval(rand2.data)))

        elif rator.data == "or":
            return Bool(str(eval(rand1.data) or eval(rand2.data)))

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
                return Err("'aug' operator expects either tuple or nil")

            if isinstance(rand2, Tup):
                rand1.symbols.extend(rand2.symbols)
            else:
                rand1.symbols.append(rand2)

            return rand1

        else:
            return Err("Unknown binary operator encountered!")

    def getStringTuple(self, tup: Tup):
        result = "("

        for symbol in tup.symbols:
            if isinstance(symbol, Tup):
                result += self.getStringTuple(symbol) + ", "

            else:
                # We need to do the following because in RPAL, truthvalues are in lowercase, but in Python, the first
                # letter is capitalized.
                data = symbol.data.lower() if isinstance(symbol, Bool) else symbol.data
                result += data + ", "

        # Remove the ', ' from the last tuple element
        result = result[0:len(result)-2] + ")"
        return result

    def getResult(self):
        self.execute()
        answer = self.stack.pop(0)

        if (isinstance(answer, Tup)):
            return self.getStringTuple(answer)

        # We need to do the following because in RPAL, truthvalues are in lowercase, but in Python, the first
        # letter is capitalized.

        return answer.data.lower() if isinstance(answer, Bool) else answer.data
