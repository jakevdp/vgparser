from parsimonious import NodeVisitor
from parsimonious.grammar import Grammar

from .node import *

__all__ = ['parse']


# Operator precedence in JS:
# https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence


VG_GRAMMAR = r"""
start = space expr1 space

###################################################
# level 1 operations: commas

expr1 = expr2 ops_expr1*
ops_expr1 = space binop_comma
binop_comma = "," space expr2

###################################################
# level 2 operations: addition & subtraction

expr2 = expr3 ops_expr2*
ops_expr2 = space (binop_add / binop_sub)
binop_add = "+" space expr3
binop_sub = "-" space expr3

###################################################
# level 3 operations: multiplication * division

expr3 = expr4 ops_expr3*
ops_expr3 = space (binop_mul / binop_div / binop_mod)
binop_mul = "*" space expr4
binop_div = "/" space expr4
binop_mod = "/" space expr4


###################################################
# level 4: unary operators

expr4 = ops_expr4* expr5
ops_expr4 = (unary_not / unary_lognot / unary_pos / unary_neg) space
unary_pos = "+" !number_start  # positive numbers are handled below
unary_neg = "-" !number_start  # negative numbers are handled below
unary_not = "!"
unary_lognot = "~"

number_start = ~r"[0-9\.]"


###################################################
# level 5: function calls

expr5 = expr6 ops_expr5*
ops_expr5 = space "(" space expr1? space")"


###################################################
# level 6: member access via "."

expr6 = expr7 ops_expr6*
ops_expr6 = space binop_getattr
binop_getattr = "." space identifier


###################################################
# level 7: parentheses
expr7 = unit / parens

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
        child = children[2]
        if isinstance(child, CommaNode):
            child = TupleNode(child)
        return child

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

    def _visit_unary(self, node, children):
        return node.expr_name.split('_')[1]

    def _visit_ops_expr(self, node, children):
        return children[1][0]

    def visit_ops_expr1(self, node, children):
        return children[1]

    def visit_expr1(self, node, children):
        term = children[0]
        for call in children[1]:
            term = CommaNode(term, call[1])
        return term

    def visit_expr4(self, node, children):
        ops, rhs = children
        print(ops, rhs)
        for op in ops[::-1]:
            rhs = UnaryOpNode(op[0], rhs)
        return rhs

    def visit_ops_expr4(self, node, children):
        return children[0]

    def visit_expr5(self, node, children):
        term = children[0]
        for call in children[1]:
            term = FunctionNode(term, *call)
        return term

    def visit_ops_expr5(self, node, children):
        args = children[3]
        if not args:
            return ()
        elif isinstance(args[0], CommaNode):
            return args[0].contents
        else:
            return (args[0],)

    def visit_ops_expr6(self, node, children):
        return children[1]

    def visit_expr7(self, node, children):
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
        if node.expr_name.startswith('unary'):
            return self._visit_unary(node, children)
        elif node.expr_name.startswith('ops_expr'):
            return self._visit_ops_expr(node, children)
        elif node.expr_name.startswith('expr'):
            return self._visit_expr(node, children)
        else:
            return children


def parse(input_string, context=None):
    context = context or {}
    grammar = VgEvaluator(context)
    return grammar.parse(input_string)
