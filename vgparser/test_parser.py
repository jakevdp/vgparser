import pytest
from . import parse


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
    assert parse(key) == val


LITERAL_TEST_CASES = {
    '_': '_',
    '_01': '_01',
    'x01_y': 'x01_y',
    'hello': 'hello',
    'Hello': 'Hello',
    'HelloThere42': 'HelloThere42',
}


@pytest.mark.parametrize("key,val", LITERAL_TEST_CASES.items())
def test_parse_literal(key, val):
    assert parse(key) == val

FUNC_TEST_CASES = {
    'sin(x)': ('sin', 'x'),
    'sin(2.0)': ('sin', 2.0),
    '_("hello")': ('_', "hello"),
    'f21(12)': ('f21', 12)
}

@pytest.mark.parametrize('key,val', FUNC_TEST_CASES.items())
def test_parse_func(key, val):
    assert parse(key) == val
