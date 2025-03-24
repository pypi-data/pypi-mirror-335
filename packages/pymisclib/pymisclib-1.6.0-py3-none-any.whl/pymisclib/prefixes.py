#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2025 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-prefixes-py
"""Convert numbers to scaled, prefixed values.

    A unit prefix is a mnemonic that comes before a unit to indicate the
    multiples or fractions of the unit. For example, 0.0001 m becomes 100 µm
    using a metric prefix. 1024 become 1 ki using a binary prefix.

    Example
    -------

    Using a metric (base 10) prefix.

    .. code-block:: python

        for n in [0, 1024, 10000, 10.5678e9, 0.1, .001234, 0.000835, 2.7e-9, ]:
            value, prefix = convert_to_prefix(n, UnitPrefix.Metric)
            print(f'{n} → {value:.2f} {prefix}')
        value, prefix = convert_to_prefix(12349)
        print(f'{value:.0f} {prefix}m')

    Output::

        0 → 0.00
        1024 → 1.02 k
        10000 → 10.00 k
        10567800000.0 → 10.57 G
        0.1 → 100.00 m
        0.001234 → 1.23 m
        0.000835 → 835.00 µ
        2.7e-09 → 2.70 n
        12 km


    Using a binary (base 2) prefix is very similar.

    .. code-block:: python

        for n in [0, 1024, 100000, 9834298724398, 42795864723858438]:
            value, prefix = convert_to_prefix(n, UnitPrefix.Binary)
            print(f'{n} ⇒ {value:.0f} {prefix}')

    Output::

        0 ⇒ 0
        1024 ⇒ 1 Ki
        100000 ⇒ 98 Ki
        9834298724398 ⇒ 9 Ti
        42795864723858438 ⇒ 38 Pi
"""

import enum
import math


@enum.unique
class UnitPrefix(enum.Enum):
    """Prefix type used to indicate fractions or multiples of a unit.

        For example, 1000 m can be expressed as 1 km using the metric prefix
        'kilo' or 'k'.
    """
    Binary = enum.auto()
    """Binary (base 2) prefix."""
    Metric = enum.auto()
    """Metric (base 10) prefix."""


"""A dictionary of prefix definitions.

    Each definition contains a dictionary with the following keys:
        - base: the base of the prefix
        - exponent: the exponent of the prefix
        - min_exponent: the minimum exponent of the prefix
        - max_exponent: the maximum exponent of the prefix
        - prefixes: the actual prefixes, ordered by rising exponent.
            All prefixes are exactly one character long.
        - long_names: a dictionary mapping each prefix to its long name.
            Each long name may be of unique length.
"""
_known_prefixes = {
    UnitPrefix.Binary: {
        'base': 1024,
        'min_exponent': 0,
        'max_exponent': 10,
        'prefixes': [
            '  ',  # 1024^0
            'Ki',  # 1024^1
            'Mi',  # 1024^2
            'Gi',  # 1024^3
            'Ti',  # 1024^4
            'Pi',  # 1024^5
            'Ei',  # 1024^6
            'Zi',  # 1024^7
            'Yi',  # 1024^8
            'Ri',  # 1024^9
            'Qi',  # 1024^10
        ],  # 'prefixes'
        'long_names': {
            '  ': '',
            'Ki': 'kibi',
            'Mi': 'mebi',
            'Gi': 'gibi',
            'Ti': 'tebi',
            'Pi': 'pebi',
            'Ei': 'exbi',
            'Zi': 'zebi',
            'Yi': 'yobi',
            'Ri': 'robi',
            'Qi': 'quebi',
        }  # 'long_names
    },  # Binary
    UnitPrefix.Metric: {
        'base': 1000,
        'min_exponent': -8,
        'max_exponent': 8,
        'prefixes': [
            'y',  # 1000^-8
            'z',  # 1000^-7
            'a',  # 1000^-6
            'f',  # 1000^-5
            'p',  # 1000^-4
            'n',  # 1000^-3
            'µ',  # 1000^-2
            'm',  # 1000^-1
            ' ',  # 1000^0
            'k',  # 1000^1
            'M',  # 1000^2
            'G',  # 1000^3
            'T',  # 1000^4
            'P',  # 1000^5
            'E',  # 1000^6
            'Z',  # 1000^7
            'Y',  # 1000^8
        ],  # prefixes
        'long_names': {
            'y': 'yocto',
            'z': 'zepto',
            'a': 'atto',
            'f': 'femto',
            'p': 'pico',
            'n': 'nano',
            'µ': 'micro',
            'm': 'milli',
            ' ': '',
            'k': 'kilo',
            'M': 'mega',
            'G': 'giga',
            'T': 'terra',
            'P': 'peta',
            'E': 'exa',
            'Z': 'zetta',
            'Y': 'yotta',
        }
    },  # Metric
}  # _known_prefixes


def convert_to_prefix(number: int | float,
                      unit_prefix: UnitPrefix = UnitPrefix.Metric) -> tuple[float, str]:
    """Convert a number to the nearest prefix.

        The nearest prefix is the one with a non-zero digit before the decimal
        separator.

        The valid range of the number depends on the prefix used.

    :param int|float number: The value to convert.
    :param UnitPrefix unit_prefix: The prefix type to use.
    :return: Converted number and prefix.
    :rtype: tuple[float, str]
    """
    pfd = _known_prefixes[unit_prefix]
    if number == 0.0:
        exponent = 0
        scaled = 0
    else:
        exponent = math.floor(math.log(math.fabs(number), pfd['base']))
        scale = math.pow(pfd['base'], exponent)
        scaled = number / scale
    if exponent > pfd['max_exponent']:
        raise ValueError('exponent too large')
    if exponent < pfd['min_exponent']:
        raise ValueError('exponent too small')
    index = exponent - pfd['min_exponent']
    return scaled, pfd['prefixes'][index]
