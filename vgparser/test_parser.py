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
    "a, b" : ('a', 'b'),
    "1, 2, 'three'": (1, 2, 'three'),
    "4 , 5 , six": (4, 5, 'six'),
}


@pytest.mark.parametrize("key,val", COMMA_TEST_CASES.items())
def test_parse_comma(key, val):
    assert parse(key) == CommaNode(*map(Node, val))


FUNC_TEST_CASES = {
    'sin(x)': ('sin', 'x'),
    'sin(2.0)': ('sin', 2.0),
    'f21(12)': ('f21', 12),
    '__("hello",\'there\')': ('__', "hello", "there"),
    'cos(x, 4)': ('cos', 'x', 4),
}


@pytest.mark.parametrize('key,val', FUNC_TEST_CASES.items())
def test_parse_func(key, val):
    args = (Node(arg) for arg in val[1:])
    assert parse(key) == FunctionNode(IdentifierNode(val[0]), *args)


GETATTR_TEST_CASES = {
    'f.x': ('f', 'x'),
}


@pytest.mark.parametrize('key,val', GETATTR_TEST_CASES.items())
def test_parse_func(key, val):
    assert parse(key) == BinOpNode('getattr',
                                   IdentifierNode(val[0]),
                                   IdentifierNode(val[1]))
