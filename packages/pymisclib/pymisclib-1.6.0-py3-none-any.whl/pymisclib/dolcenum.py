#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-dolcenum-py
"""Enum metaclass to assign member docstrings to the members.

The idea was found at https://stackoverflow.com/a/78943193.
"""

import enum
import inspect
from typing import Self, Type


class MissingDocstringError(Exception):
    """DoclEnumMeta-derived enum is missing one or more docstrings."""
    pass


class DolcEnumMeta(enum.EnumMeta):
    """Metaclass to assign member docstrings to the enum members.

    The metaclass is assigned to the `metaclass` attribute in the enum class
    definition. The class itself and each member **must** have a docstring
    (or there must be **no** docstrings whatsoever.)

    :raise ValueError: One or more docstrings are missing.

    Example
    -------

    .. code-block:: python

        import enum
        from pymisclib.dolcenum import DolcEnumMeta


        @enum.unique
        class MyEnum(enum.IntEnum, metaclass=DolcEnumMeta):
            \"\"\"Class MyEnum docstring.\"\"\"
            A = enum.auto()
            \"\"\"Member MyEnum.A docstring.\"\"\"
            B = enum.auto()
            \"\"\"Member MyEnum.B docstring.\"\"\"
            C = enum.auto()
            \"\"\"Member MyEnum.C docstring.\"\"\"


        for e in MyEnum:
            print(f'{e.name}:{e.value} "{e.__doc__}"')
    """
    def __new__(metaclass: Type[Self], name: str, bases: tuple[type, ...], attrs: enum._EnumDict):
        """Create a new instance with docstrings for each member."""
        cls = super().__new__(metaclass, name, bases, attrs)

        # Get the source code and split comment into individual docstrings.
        source = inspect.getsource(cls)
        docstrings = source.split('"""')[-2::-2]

        if len(docstrings) == 0:
            # No docstrings means nothing to do.
            return cls
        # Check for consistency.
        if len(docstrings) < len(cls.__members__) + 1:
            raise MissingDocstringError('missing docstring')

        # Assign a docstring to each member.
        for member_name, member_docstring in zip(reversed(cls.__members__), docstrings):
            enum_member = getattr(cls, member_name, None)
            enum_member.__doc__ = member_docstring.strip()

        return cls


def example():

    @enum.unique
    class Enum1(enum.Enum, metaclass=DolcEnumMeta):
        """Enum1 class docstring."""
        E1 = enum.auto()
        """Enum1.E1 member docstring."""
        E2 = enum.auto()
        """Enum1.E2 member docstring."""
        E3 = enum.auto()
        """Enum1.E3 member docstring."""

    print('Enum1 has a docstring per member.')
    for e in Enum1:
        print(f'    {e.name}:{e.value} "{e.__doc__}"')

    try:
        @enum.unique
        class Enum2(enum.Enum, metaclass=DolcEnumMeta):
            """Enum2 class docstring."""
            E1 = enum.auto()
            """Enum2.E1 member docstring."""
            E2 = enum.auto()
            """Enum2.E2 member docstring."""
            E3 = enum.auto()

        print('Enum2 is missing the last docstring.')
        for e in Enum2:
            print(f'    {e.name}: {e.__doc__}')
    except MissingDocstringError as e:
        print(f'Missing docstring detected: {e}')


if __name__ == '__main__':
    example()

