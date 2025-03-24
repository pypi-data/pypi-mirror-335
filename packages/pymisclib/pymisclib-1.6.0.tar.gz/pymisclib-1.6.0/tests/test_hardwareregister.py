#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-hardwareregister-py
import enum
from typing import Tuple

import pytest

from pymisclib.hardwareregister import (
    Register, RegisterDescription, RegisterFieldBool, RegisterFieldEnum,
    RegisterFieldInt, RegisterValue)


@pytest.mark.parametrize('bit', [x for x in range(0, 64)])
def test_register_field_bool(bit: int):
    fb = RegisterFieldBool('fb', bit)
    assert isinstance(fb, RegisterFieldBool)
    assert fb.name == 'fb'
    assert fb.conversion == bool
    assert fb.first_bit == fb.last_bit
    assert fb.first_bit == bit
    assert fb.mask == (1 << bit)
    assert fb.convert(0) == False
    assert fb.convert(1) == True


def bit_ranges() -> Tuple[int, int]:
    for x in range(0, 64):
        for y in range(x, 64):
            yield x, y

@pytest.mark.parametrize('first_bit, last_bit', [x for x in bit_ranges()])
def test_register_field_int_ok(first_bit: int, last_bit: int):
    f_int = RegisterFieldInt('f_int', first_bit, last_bit)
    assert isinstance(f_int, RegisterFieldInt)
    assert f_int.name == 'f_int'
    assert f_int.conversion == int
    assert f_int.first_bit == first_bit
    assert f_int.last_bit == last_bit
    assert f_int.min_value == 0
    assert f_int.max_value == (1 << (last_bit - first_bit + 1)) - 1
    assert f_int.mask == ((1 << (last_bit + 1)) - 1) & ~((1 << first_bit) - 1)
    assert f_int.convert((1 << first_bit) - last_bit) == (1 << first_bit) - last_bit


def test_register_field_int_bit_range_error():
    with pytest.raises(IndexError):
        RegisterFieldInt('f8', 1, 0)


def test_register_field_int_enum():
    @enum.unique
    class E1(enum.IntEnum):
        zero = 0
        one = 1
        two = 2
        three = 3

    f_ie = RegisterFieldEnum('f_ie', 7, 8, E1)
    assert isinstance(f_ie, RegisterFieldEnum)
    assert f_ie.name == 'f_ie'
    assert f_ie.conversion == E1
    assert f_ie.first_bit == 7
    assert f_ie.last_bit == 8
    assert f_ie.mask == 0x180
    assert f_ie.convert(0) == E1.zero
    assert f_ie.convert(1) == E1.one
    assert f_ie.convert(2) == E1.two
    assert f_ie.convert(3) == E1.three


def test_register_description():
    rd = RegisterDescription(
        32,
        [RegisterFieldBool('b0', 0),
         RegisterFieldInt('i1_17', 1, 17),
         RegisterFieldInt('i18_21', 18, 21),
         # Bits 21..30 are reserved
         RegisterFieldBool('b31', 31)])

def test_register_description_bit_order():
    total_bits = 32
    rd = RegisterDescription(
        total_bits,
        [RegisterFieldBool('b0', 0),
         RegisterFieldInt('i18_21', 18, 21),
         RegisterFieldInt('i1_17', 1, 17),
         # Bits 21..30 are reserved
         RegisterFieldBool('b31', 31)])
    current_bit = -1
    for field in rd.fields_by_start_bit():
        assert current_bit < field.first_bit
        current_bit = field.last_bit
    assert current_bit < total_bits
    current_bit = total_bits
    for field in rd.fields_by_end_bit():
        assert current_bit > field.last_bit
        current_bit = field.first_bit
    assert current_bit >= 0

def test_register():
    rd = RegisterDescription(
        32,
        [RegisterFieldBool('b0', 0),
         RegisterFieldInt('i1_17', 1, 17),
         RegisterFieldInt('i18_21', 18, 21),
         # Bits 21..30 are reserved
         RegisterFieldBool('b31', 31)])
    reg = Register('register1@0x123', 0x123, rd)


def test_register_value():
    @enum.unique
    class E2(enum.IntFlag):
        b0 = 1
        b1 = 2
        b2 = 4

    rd = RegisterDescription(
        32,
        [RegisterFieldBool('b0', 0),
         RegisterFieldInt('i1_17', 1, 17),
         RegisterFieldInt('i18_21', 18, 21),
         RegisterFieldEnum('e22_24', 22, 24, E2),
         # Bits 25..30 are reserved
         RegisterFieldBool('b31', 31)])
    rv = RegisterValue('register1@0', 0, rd, value=0x80fe2345)
    # 31     24      16       8       0
    #          --------        --------
    #  10000000111111100010001101000101
    #  b31       i18 i1_17            b0
    assert rv.value == 0x80fe2345
    assert rv.b0 == True
    assert rv.i1_17 == 0x111a2
    assert rv.i18_21 == 0xf
    assert rv.e22_24 == E2.b0 | E2.b1
    assert rv.b31 == True
    rv.set('b0', False)
    assert rv.value == 0x80fe2344
    rv.set('i1_17', 0x11a2)
    assert rv.value == 0x80fc2344
    rv.set('e22_24', E2.b2)
    assert rv.value == 0x813c2344
