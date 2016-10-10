import pytest
from . import parse
from .node import *

NUMBER_TEST_CASES = {
    # decimal integers
    '12345': 12345,
    '+100': 100,
    '-42': -42,

    # binary integers
    '0b11': 0b11,
    '-0b101': -0b101,
    '0B01': 0b01,
    '-0B001': -0b001,

    # octal integers
    '012': 0o12,
    '-0132': -0o132,
    '0o12': 0o12,
    '-0o132': -0o132,
    '0O12': 0o12,
    '-0O132': -0o132,

    # hexadecimal integers
    '0x42': 0x42,
    '-0xFA': -0xFA,
    '0X0F0': 0x0F0,
    '-0X5DEF': -0x5DEF,
    '0x42': 0x42,
    '-0xFA': -0xfA,
    '0X0F0': 0x0f0,
    '-0X5DEF': -0x5DeF,

    # floating point
    '11.': 11.0,
    '0E5': 0.0,
    '012E02': 12E2,
    '1.1': 1.1,
    '0.1': 0.1,
    '+.1': 0.1,
    '.11': 0.11,
    '1E4': 1E4,
    '1.2E-3': 1.2E-3,
    '-1E-4': -1E-4,
    '-1.2E-3': -1.2E-3,
    '12e4': 12E4,
    '1.22e-3': 1.22E-3,
    '-12e-4': -12E-4,
    '-1.22e-3': -1.22E-3,
}


@pytest.mark.parametrize("key,val", NUMBER_TEST_CASES.items())
def test_parse_number(key, val):
    assert parse(key) == NumberNode(val)


IDENTIFIER_TEST_CASES = {
    '_': '_',
    '_01': '_01',
    'x01_y': 'x01_y',
    'hello': 'hello',
    'Hello': 'Hello',
    'HelloThere42': 'HelloThere42',
}


@pytest.mark.parametrize("key,val", IDENTIFIER_TEST_CASES.items())
def test_parse_identifier(key, val):
    assert parse(key) == IdentifierNode(val)


STRING_TEST_CASES = {
    '"abc def ghi 123\t\n"': 'abc def ghi 123\t\n',
    "'abc def ghi 123'": 'abc def ghi 123',
    "'hello \"there\"'": 'hello "there"',
    '"hello \'there\'"': "hello 'there'",
}


@pytest.mark.parametrize("key,val", STRING_TEST_CASES.items())
def test_parse_string(key, val):
    assert parse(key) == StringNode(val)


COMMA_TEST_CASES = {
    "a, b" : CommaNode(IdentifierNode('a'), IdentifierNode('b')),
    "1, 2, 'three'": CommaNode(NumberNode(1), NumberNode(2),
                               StringNode('three')),
    "4 , 5 , six": CommaNode(NumberNode(4), NumberNode(5),
                             IdentifierNode('six')),
}


@pytest.mark.parametrize("key,val", COMMA_TEST_CASES.items())
def test_parse_comma(key, val):
    assert parse(key) == val


ARITH_TEST_CASES = {
    "a + 4": BinOpNode('add', IdentifierNode('a'), NumberNode(4)),
    "a- '5'": BinOpNode('sub', IdentifierNode('a'), StringNode('5')),
    "a *b": BinOpNode('mul', IdentifierNode('a'), IdentifierNode('b')),
    "a   /   7.0": BinOpNode('div', IdentifierNode('a'), NumberNode(7.0)),
    "3 + 4 * 5": BinOpNode("add", NumberNode(3),
                           BinOpNode("mul", NumberNode(4), NumberNode(5))),
    "(3 + 4) * 5": BinOpNode("mul",
                             BinOpNode("add", NumberNode(3), NumberNode(4)),
                             NumberNode(5)),
    "3 + 4 - 5": BinOpNode("sub",
                           BinOpNode("add", NumberNode(3), NumberNode(4)),
                           NumberNode(5)),
    "3 + (4 - -5)": BinOpNode("add", NumberNode(3),
                              BinOpNode("sub", NumberNode(4), NumberNode(-5))),
    "3 + 4 * -5": BinOpNode("add", NumberNode(3),
                            BinOpNode("mul", NumberNode(4), NumberNode(-5))),
    "(3 + 4) * -5": BinOpNode("mul",
                              BinOpNode("add", NumberNode(3), NumberNode(4)),
                              NumberNode(-5)),
    "3 + 4 - -5": BinOpNode("sub",
                            BinOpNode("add", NumberNode(3), NumberNode(4)),
                            NumberNode(-5)),
    "3 + (4 - -5)": BinOpNode("add", NumberNode(3),
                              BinOpNode("sub", NumberNode(4), NumberNode(-5)))
}


@pytest.mark.parametrize("key,val", ARITH_TEST_CASES.items())
def test_parse_arithmetic(key, val):
    assert parse(key) == val


FUNC_TEST_CASES = {
    'sin(x)': FunctionNode(IdentifierNode('sin'), IdentifierNode('x')),
    'sin(2.0)': FunctionNode(IdentifierNode('sin'), NumberNode(2.0)),
    'f21(12)': FunctionNode(IdentifierNode('f21'), NumberNode(12)),
    '__("hello",\'there\')': FunctionNode(IdentifierNode('__'),
                                      StringNode("hello"),
                                      StringNode("there")),
    'cos(x, 4)': FunctionNode(IdentifierNode('cos'), IdentifierNode('x'),
                          NumberNode(4)),
}


@pytest.mark.parametrize('key,val', FUNC_TEST_CASES.items())
def test_parse_func(key, val):
    assert parse(key) == val


GETATTR_TEST_CASES = {
    'f.x': BinOpNode('getattr',
                     IdentifierNode('f'),
                     IdentifierNode('x')),
    'f.x.y': BinOpNode('getattr',
                       BinOpNode('getattr',
                                 IdentifierNode('f'),
                                 IdentifierNode('x')),
                     IdentifierNode('y')),
}


@pytest.mark.parametrize('key,val', GETATTR_TEST_CASES.items())
def test_parse_getattr(key, val):
    assert parse(key) == val
