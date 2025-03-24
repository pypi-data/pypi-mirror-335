#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024, 2025 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-hardwareregister-py
"""Description of hardware registers.

    A register has a name and an offset (which can be an address).

    A register is made up of one or more fields. A field starts at a (low)
    first bit and ends as a last (high) bit. The bit range is inclusive.

    The bits in the field can be converted to several types:
        - boolean (one bit only)
        - enum
        - integer (unsigned)

    A register can have a value.
"""
from collections import OrderedDict
import enum
import sys
from typing import Any, Generator, Type, TypeVar


class RegisterField:
    """Describe a field in a register."""

    def __init__(self, name: str,
                 first_bit: int = 0,
                 last_bit: int = 31,
                 conversion: Type = None):
        """Initialize the instance.

        :param name: The name of the field.
        :param first_bit: The first bit of the register belonging to the field (inclusive).
        :param last_bit: The last bit of the register belonging to the field (inclusive).
        :param TypeVar conversion: The conversion class.
        :raise IndexError: last_bit is smaller than first_bit.
        """
        self._name = name
        if first_bit > last_bit:
            raise IndexError("first bit larger than last bit")
        self._first_bit = first_bit
        self._last_bit = last_bit
        self._conversion = conversion

    def __str__(self) -> str:
        s = f'<{self.__class__.__name__}: {self._name} [{self._first_bit}'
        if self._first_bit == self._last_bit:
            s += '] '
        else:
            s += f':{self.last_bit}] '
        if self._conversion is not None:
            s += f'{self._conversion.__name__}'
        else:
            s += 'None'
        s += '>'
        return s

    @property
    def conversion(self) -> Type:
        """Return class used to convert the value."""
        return self._conversion

    @property
    def name(self) -> str:
        """Name of the field."""
        return self._name

    @property
    def type(self) -> Type:
        """Type of the field."""
        return self._conversion

    @property
    def first_bit(self) -> int:
        """First bit of the register containing the field."""
        return self._first_bit

    @property
    def last_bit(self) -> int:
        """Last bit of the register containing the field."""
        return self._last_bit

    @property
    def mask(self) -> int:
        """A mask leaving only bits contained in the field."""
        left = (1 << (self._last_bit + 1)) - 1
        right = (1 << self._first_bit) - 1
        return left & ~right

    def convert(self, value: Any) -> Any:
        """Convert the given value to the type of the field."""
        return self._conversion(value)


class RegisterFieldBool(RegisterField):
    """A field in a register that is a single bit."""

    def __init__(self, name: str, bit: int):
        """Initialize the instance.

        :param str name: Name of the field.
        :param int bit: The bit in the register of the field.
        """
        super().__init__(name, bit, bit, bool)


class RegisterFieldInt(RegisterField):
    """A register field containing an integral value."""

    def __init__(self, name: str, first_bit: int, last_bit: int):
        """Initialize the instance.

        :param str name: Name of the field.
        :param int first_bit: First bit of the register containing the field (inclusive).
        :param int last_bit: Last bit of the register containing the field (inclusive).
        """
        super().__init__(name, first_bit, last_bit, int)
        self._min_value = 0
        self._max_value = (1 << (last_bit + 1 - first_bit)) - 1

    @property
    def min_value(self) -> int:
        """Minimum allowed value in the field (inclusive)."""
        return self._min_value

    @property
    def max_value(self) -> int:
        """Maximum allowed value in the field (inclusive)."""
        return self._max_value


class RegisterFieldEnum(RegisterField):
    def __init__(self, name: str, first_bit: int, last_bit: int, conversion: Type[enum.IntEnum]|Type[enum.IntFlag]):
        """Initialize the instance.

        :param str name: Name of the field.
        :param int first_bit: First bit of the register containing the field (inclusive).
        :param int last_bit: Last bit of the register containing the field (inclusive).
        :param TypeVar conversion: The conversion class which must be an enum.
        """
        super().__init__(name, first_bit, last_bit, conversion)


class RegisterDescription:
    """Describes the layout and fields of a register."""

    def __init__(self, nr_bits: int, fields: list[RegisterField]):
        """Initialize self.

        :param int nr_bits: Number of bits in the register.
        :param list[RegisterField] fields: Fields of the register.
        :raise IndexError: An error was found in the fields.
        :raise KeyError: A field name was used multiple times.
        """
        self._nr_bits = nr_bits
        self._fields_by_name = OrderedDict([(f.name, f) for f in sorted(fields, key=lambda field: field.name)])
        self._fields_by_start = OrderedDict([(f.first_bit, f) for f in sorted(fields, key=lambda field: field.first_bit)])
        # Make sure fields are sorted by rising first_bit.
        self._fields = self._fields_by_start.values()
        if len(self._fields) != len(self._fields_by_name):
            raise KeyError('field name multiply defined')
        if len(self._fields) != len(self._fields_by_start):
            raise KeyError('field position multiply defined')
        self.check_field_consistency()

    def __str__(self) -> str:
        """Convert instance to a human-readable string.

            :rtype: str
        """
        s = f'<{self.__class__.__name__} nr_bits:{self._nr_bits}' +\
            f' fields:['
        first = True
        for first_bit in sorted(self._fields_by_start.keys()):
            field = self._fields_by_start[first_bit]
            if not first:
                s += f', {field}'
            else:
                s += f'{field}'
                first = False
        s += ']>'
        return s

    def check_field_consistency(self):
        """Check that the fields are consistently defined.

        :raise IndexError: An error was found in the fields.
        """
        nr_bits = 0
        bit_offset = -1
        for field in self._fields:
            if bit_offset >= field.first_bit:
                raise IndexError('bits multiply defined')
            nr_bits += field.first_bit - field.last_bit + 1
            if nr_bits > self._nr_bits:
                raise IndexError('too many bits')

    def field(self, name: str) -> RegisterField:
        """Return the field with the given name.

            :param str name: Name of the field.
            :raise KeyError: The given name is not a field.
        """
        return self._fields_by_name[name]

    def fields_by_start_bit(self) -> Generator[RegisterField, None, None]:
        """Yield all register fields in rising order of their start bit.

            :return: A register field per call.
            :rtype: RegisterField
        """
        for field in self._fields:
            yield field

    def fields_by_end_bit(self) -> Generator[RegisterField, None, None]:
        """Yield all register fields in falling order of their end bit.

            :return: A register field per call.
            :rtype: RegisterField
        """
        for field in reversed(self._fields):
            yield field

    def mask_keep_field(self, field: RegisterField) -> int:
        """Create a mask to remove all bits not belonging to the field.

           :param RegisterField field: The field to mask.
           :return: A mask leaving only the bits belonging to the field.
        """
        return field.mask

    def mask_remove_field(self, field: RegisterField) -> int:
        """Create a mask to remove all bits belonging to the field.

            :param RegisterField field: The field to mask.
            :return: A mask removing all bits belonging to the field.
        """
        return ~field.mask


class Register:
    """A register at an offset with a name and description."""

    def __init__(self, name: str, offset: int, description: RegisterDescription):
        """Initialize self.

        :param str name: Name of the register.
        :param int offset: Offset of the register.
        :param RegisterDescription description: Description of the register.
        """
        self._name = name
        self._offset = offset
        self._description = description

    def __str__(self) -> str:
        """Convert instance to a human-readable string.

            :rtype: str
        """
        s = f'<{self.__class__.__name__}:{self._name}' + \
            f' offset:0x{self._offset:0x} {self._description}>'
        return s

    @property
    def name(self) -> str:
        """Return the register name."""
        return self._name

    @property
    def offset(self) -> int:
        """Offset of the register in memory."""
        return self._offset

    @property
    def description(self) -> RegisterDescription:
        """Description of the register."""
        return self._description


class RegisterValue(Register):
    def __init__(self, name: str,
                 offset: int,
                 description: RegisterDescription,
                 value: int):
        super().__init__(name, offset, description)
        self._value = value

    @property
    def value(self) -> int:
        """Return the register value as an integer."""
        return self._value

    @value.setter
    def value(self, value: int):
        """Set the register integer value."""
        self._value = value

    def __getattr__(self, name: str) -> bool|int|enum.IntEnum|enum.IntFlag:
        """Get the value of the named field in the register.

        :param str name: Name of the field.
        :rtype: bool|int|enum.IntEnum|enum.IntFlag
        :return: Value of the field in the register.
        :raise AttributeError: the field does not exist.
        """
        the_field = self._description.field(name)
        value = (self._value & the_field.mask) >> the_field.first_bit
        return the_field.convert(value)

    def set(self, name: str, value: bool|int|enum.IntEnum|enum.IntFlag):
        """Set the value of the named field in the register.

        :param str name: Name of the field.
        :param bool|int|enum.IntEnum|enum.IntFlag value: Value of the field in the register.
        :raise AttributeError: the field does not exist.
        """
        the_field = self._description.field(name)
        v = int(value) << the_field.first_bit
        self._value = (self._value & ~the_field.mask) | v


def example():
    """Module demonstration."""
    wdt_ctrla = Register('WDT CTRLA', 0x0100,
                         RegisterDescription( 8, [
                             RegisterFieldInt('PERIOD', 0, 3),
                             RegisterFieldInt('WINDOW', 4, 7)])
                         )
    print(f'wdt_ctrla contains integer fields: {wdt_ctrla}')
    wdt_status = Register('WDT STATUS', 0x0101,
                          RegisterDescription(8, [
                              RegisterFieldBool('SYNCBUSY', 0),
                              RegisterFieldBool('LOCK', 7)])
                          )
    print(f'wdt_status contains boolean fields: {wdt_status}')

    @enum.unique
    class VrefAC0RegSel(enum.IntEnum):
        """"""
        V0_55 = 0x00
        """0.55V"""
        V1_1  = 0x01
        """1.1V"""
        V2_5  = 0x02
        """2.5V"""
        V4_4  = 0x04
        """4.4V"""
        res1  = 0x05
        """Reserved"""
        res2  = 0x06
        """Reserved"""
        AVDD  = 0x07
        """AVDD"""

    vref_ctrla = Register('VREF CTRLA', 0x00A0,
                          RegisterDescription(8, [
                              RegisterFieldEnum('AC0REFSEL', 0, 2, VrefAC0RegSel)])
                          )
    print(f'vref_ctrla contains enum fields: {vref_ctrla}')


if __name__ == '__main__':
    if sys.version_info < (3, 10):
        print('FATAL ERROR: Python 3.10.x or later is required.')
        sys.exit(1)
    example()
