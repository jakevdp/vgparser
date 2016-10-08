from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

from .node import *

__all__ = ['parse']


# Operator precedence in JS:
# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence


VG_GRAMMAR = r"""
start = space expr1 space

###################################################
# level 1 operations: addition & subtraction

expr1 = expr2 ops_level_1*
ops_level_1 = space (binop_add / binop_sub)
binop_add = "+" space expr2
binop_sub = "-" space expr2

###################################################
# level 2 operations: multiplication * division

expr2 = expr3 ops_level_2*
ops_level_2 = space (binop_mul / binop_div)
binop_mul = "*" space expr3
binop_div = "/" space expr3

###################################################
# level 3: function calls

expr3 = expr4 ops_level_3*
ops_level_3 = space (parens / empty_parens)
empty_parens = "(" space ")"

###################################################
# level 4: member access via "."

expr4 = expr5 ops_level_4*
ops_level_4 = space binop_getattr
binop_getattr = "." space identifier


###################################################
# level 5: parentheses
expr5 = unit / parens

parens = ("(" space expr1 space ")")

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

class VgEvaluator(NodeVisitor):
    def __init__(self, ctx=None, strict=True):
        self.grammar = Grammar(VG_GRAMMAR)
        self._ctx = ctx or {}
        self._strict = strict

    def visit_start(self, node, children):
        return children[1]

    def visit_parens(self, node, children):
        return children[2]

    def visit_term(self, node, children):
        return children[0]

    def visit_integer(self, node, children):
        return IntegerNode(int(node.text))

    def visit_identifier(self, node, children):
        return IdentifierNode(node.text)

    def _visit_expr(self, node, children):
        lhs, ops = children
        for op, rhs in ops:
            lhs = BinOpNode(op, lhs, rhs)
        return lhs

    def _visit_binop(self, node, children):
        return (node.expr_name.split('_')[1], children[2])

    def _visit_ops_level(self, node, children):
        return children[1][0]

    def visit_ops_level_4(self, node, children):
        return children[1]

    def visit_expr3(self, node, children):
        term = children[0]
        for call in children[1]:
            term = FunctionNode(term, call)
        return term

    def visit_expr5(self, node, children):
        return children[0]

    def visit_unit(self, node, children):
        return children[0]

    def visit_identifier(self, node, children):
        return IdentifierNode(node.text)

    def visit_string(self, node, children):
        return StringNode(node.match.groups()[1])

    def visit_number(self, node, children):
        return children[0]

    def visit_float(self, node, children):
        return NumberNode(float(node.text))

    def visit_hexadecimal(self, node, children):
        return NumberNode(int(node.text, 16))

    def visit_binary(self, node, children):
        return NumberNode(int(node.text, 2))

    def visit_octal(self, node, children):
        return NumberNode(int(node.text, 8))

    def visit_integer(self, node, children):
        return NumberNode(int(node.text))

    def generic_visit(self, node, children):
        if node.expr_name.startswith('binop'):
            return self._visit_binop(node, children)
        elif node.expr_name.startswith('ops_level'):
            return self._visit_ops_level(node, children)
        elif node.expr_name.startswith('expr'):
            return self._visit_expr(node, children)
        else:
            return children


def parse(input_string, context=None):
    context = context or {}
    grammar = VgEvaluator(context)
    return grammar.parse(input_string)
