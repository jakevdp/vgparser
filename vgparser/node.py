class Node(object):
    def __init__(self, *contents):
        self.contents = contents

    def __repr__(self):
        return "<{0} {1}>".format(self.__class__.__name__,
                                  ', '.join(map(repr, self.contents)))

    def __eq__(self, other):
        same_class = (isinstance(other, self.__class__)
                      or isinstance(self, other.__class__))
        return same_class and self.contents == other.contents


class UnitNode(Node):
    def __repr__(self):
        return repr(self.contents[0])


class NumberNode(UnitNode):
    pass


class StringNode(UnitNode):
    def __repr__(self):
        return repr(self.contents[0])


class IdentifierNode(UnitNode):
    def __repr__(self):
        return self.contents[0]


class FunctionNode(Node):
    def __init__(self, func, *arguments):
        super(FunctionNode, self).__init__(func, *arguments)
        self.func = func
        self.arguments = arguments

    def __repr__(self):
        return "{0}({1})".format(repr(self.func),
                                 ', '.join(map(repr, self.arguments)))


class BinOpNode(FunctionNode):
    def __init__(self, opname, *arguments):
        super(FunctionNode, self).__init__(opname, *arguments)
        self.func = IdentifierNode('binop.' + opname)
        self.arguments = arguments
