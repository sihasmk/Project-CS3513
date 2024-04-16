from NodeFactory import NodeFactory


class Node:
    def __init__(self) -> None:
        self.data = ""
        self.depth = 0
        self.parent = None
        self.children = []
        self.isStandardized = False

    def standardize(self):
        if not self.isStandardized:
            for child in self.children:
                child.standardize()

            # In accordance with CSE Rules 6 - 11, we don't standardize "tau", "UOp", "BOp", ",", and "->" nodes

            match self.data:
                # Standardizing "let" node
                case "let":
                    E = self.children[0].children[1]
                    E.parent = self
                    E.depth = self.depth + 1
                    P = self.children[1]
                    P.parent = self.children[0]
                    P.depth = self.depth + 2
                    self.children[0].data = "lambda"
                    self.children[1] = E
                    self.children[0].children[1] = P
                    self.data = "gamma"

                # Standardizing "where" node
                case "where":
                    # Here, we can simply convert the "where" node into a "let" node and standardize it as above
                    P = self.children[0]
                    self.children[0] = self.children[1]
                    self.children[1] = P

                    self.data = "let"
                    self.standardize()

                case "function_form":
                    E = self.children[len(self.children)-1]
                    lambda_node = NodeFactory.getNode(
                        "lambda", self.depth + 1, self, [], True)

                    # We can set isStandardized of this node to True, because since
                    # we start standardization from the leaf nodes, E will already
                    # be standardized.

                    self.children.insert(1, lambda_node)

                    while self.children[2] != E:
                        V = self.children.pop(2)
                        V.depth = lambda_node.depth + 1
                        V.parent = lambda_node
                        lambda_node.children.append(V)

                        if len(self.children) > 3:
                            lambda_node = NodeFactory.getNode(
                                "lambda", lambda_node.depth + 1, lambda_node, [], True)
                            lambda_node.parent.children.append(lambda_node)

                    lambda_node.children.append(E)

                    # Remove E from children of the fcn_form
                    self.children.pop(2)
                    self.data = "="

                case "lambda":
                    degree = len(self.children)

                    if degree > 2:
                        E = self.children[degree-1]

                        lambda_node = NodeFactory.getNode(
                            "lambda", self.depth + 1, self, [], True)
                        self.children.insert(1, lambda_node)

                        while self.children[2] != E:
                            V = self.children.pop(2)
                            V.depth = lambda_node.depth + 1
                            V.parent = lambda_node
                            lambda_node.children.append(V)

                            if len(self.children) > 3:
                                lambda_node = NodeFactory.getNode(
                                    "lambda", lambda_node.depth + 1, lambda_node, [], True)
                                lambda_node.parent.children.append(lambda_node)

                        lambda_node.children.append(E)

                        # Remove the E from the starting lambda node
                        self.children.pop(2)

                case "within":
                    X1 = self.children[0].children[0]
                    E1 = self.children[0].children[1]
                    X2 = self.children[1].children[0]
                    E2 = self.children[1].children[1]

                    gamma = NodeFactory.getNode(
                        "gamma", self.depth + 1, self, [], True)
                    lambda_node = NodeFactory.getNode(
                        "lambda", self.depth + 2, gamma, [], True)

                    X1.depth += 1
                    X1.parent = lambda_node

                    X2.depth -= 1
                    X2.parent = self

                    E1.parent = gamma

                    E2.depth += 1
                    E2.parent = lambda_node

                    lambda_node.children.append(X1)
                    lambda_node.children.append(E2)

                    gamma.children.append(lambda_node)
                    gamma.children.append(E1)

                    self.children.clear()
                    self.children.append(X2)
                    self.children.append(gamma)

                    self.data = "="

                case "@":
                    E1 = self.children[0]
                    N = self.children[1]
                    E2 = self.children[2]

                    bottom_gamma = NodeFactory(
                        "gamma", self.depth+1, self, [], True)

                    E1.depth += 1
                    N.depth += 1

                    N.parent = bottom_gamma
                    E1.parent = bottom_gamma
                    E2.parent = self

                    bottom_gamma.children.append(N)
                    bottom_gamma.children.append(E1)

                    self.children.pop(0)
                    self.children.pop(0)
                    self.children.insert(0, bottom_gamma)

                    self.data = "gamma"

                case "and":
                    Xs = []
                    Es = []

                    comma = NodeFactory.getNode(
                        ",", self.depth + 1, self, [], True)
                    tau = NodeFactory.getNode(
                        "tau", self.depth + 1, self, [], True)

                    for equal in self.children:
                        # No need to change depths of E's and X's, but we do need to change their parents
                        equal.children[0].parent = comma
                        equal.children[1].parent = tau

                        Xs.append(equal.children[0])
                        Es.append(equal.children[1])

                    comma.children = Xs
                    tau.children = Es

                    self.children.clear()
                    self.children.extend([comma, tau])

                    self.data = "="

                case "rec":
                    pass

        self.isStandardized = True
