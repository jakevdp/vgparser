from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

__all__ = ['parse']


GRAMMAR = r"""
#########################################################
# Identifiers and functions
function = (identifier space "(" unit ")") / unit


#########################################################
## Unit is a single quantity like a string, float, or variable identifier

unit = number / string / identifier

identifier = ~"[_a-zA-Z][_a-zA-Z0-9]*"

string = ~r"([\'\"])([^\1]*)\1"   # TODO: handle excaped chars

number = float / hexadecimal / binary / octal / integer

float = exponent_float / decimal_float

exponent_float = (decimal_float / integer_part) ("E" / "e") integer_part

decimal_float = ~r"[+-]?([0-9]+[.][0-9]*|[.][0-9]+)"

hexadecimal = ~r"[+-]?0[Xx][0-9A-Fa-f]+"

binary = ~r"[+-]?0[Bb][0-1]+"

octal = ~r"[+-]?0[Oo]?[0-7]+"

integer = ~r"[+-]?[1-9][0-9]*"  # integers cannot start with 0 (indicates octal)

# building blocks
space = " "*
integer_part = ~r"[+-]?[0-9]+"
"""

# Operator precedence in JS:
# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence


class Node(object):
    def __init__(self, *contents):
        self.contents = contents

    def __eq__(self, other):
        same_class = (isinstance(other, self.__class__)
                      or isinstance(self, other.__class__))
        return same_class and self.contents == other.contents


class JSEvaluator(NodeVisitor):
    def __init__(self, ctx, strict=True):
        self.grammar = Grammar(GRAMMAR)
        self._ctx = ctx
        self._strict = strict

    def visit_function(self, node, children):
        child = children[0]
        if isinstance(child, Node):
            return child
        else:
            return Node(child[0], child[3])

    def visit_unit(self, node, children):
        return children[0]

    def visit_identifier(self, node, children):
        return Node(node.text)

    def visit_string(self, node, children):
        return Node(node.match.groups()[1])

    def visit_number(self, node, children):
        return children[0]

    def visit_float(self, node, children):
        return Node(float(node.text))

    def visit_hexadecimal(self, node, children):
        return Node(int(node.text, 16))

    def visit_binary(self, node, children):
        return Node(int(node.text, 2))

    def visit_octal(self, node, children):
        return Node(int(node.text, 8))

    def visit_integer(self, node, children):
        return Node(int(node.text))

    def generic_visit(self, node, children):
        return children


def parse(input_string, context=None):
    context = context or {}
    grammar = JSEvaluator(context)
    return grammar.parse(input_string)
