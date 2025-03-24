#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2025 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-utilities-convert-to-si

from dataclasses import dataclass
import math

import pytest
from pymisclib.prefixes import convert_to_prefix, UnitPrefix


@dataclass
class TestVector:
    """Test vector to test conversion to SI-prefixed."""
    value: float
    """Value to convert."""
    expected_scaled: float
    """Expected scaled value."""
    expected_prefix: str
    """Expected metric prefix."""


test_vectors_binary_selected = [
    TestVector(0, 0, '  '),  # trivial
    TestVector(1, 1, '  '),  # also trivial
    # Progression of values.
    TestVector(1.073741824, 1.073741824, '  '),
    TestVector(10.73741824, 10.73741824, '  '),
    TestVector(107.3741824, 107.3741824, '  '),
    TestVector(1073.741824, 1.048576, 'Ki'),
    TestVector(10737.41824, 10.48576, 'Ki'),
    TestVector(107374.1824, 104.8576, 'Ki'),
    TestVector(1073741.824, 1.024, 'Mi'),
    TestVector(10737418.24, 10.24, 'Mi'),
    TestVector(107374182.4, 102.4, 'Mi'),
    TestVector(1073741824, 1, 'Gi'),
    # Test around the switch from Mi to Gi
    TestVector(1073741823, 1023.999999, 'Mi'),
    TestVector(1073741824, 1, 'Gi'),
    TestVector(1073741825, 1, 'Gi'),
]  # test_vectors_binary_selected

test_vectors_metric_selected = [
    TestVector(0, 0, ' '),  # trivial test
    TestVector(1, 1, ' '),  # another trivial test
    # test a progression of values
    TestVector(1.2356494, 1.2356494, ' '),
    TestVector(12.356494, 12.356494, ' '),
    TestVector(123.56494, 123.56494, ' '),
    TestVector(1235.6494, 1.2356494, 'k'),
    TestVector(12356.494, 12.356494, 'k'),
    TestVector(123564.94, 123.56494, 'k'),
    TestVector(1235649.4, 1.2356494, 'M'),
    # test around the switch from M to G
    TestVector(999999999, 999.999999, 'M'),
    TestVector(1000000000, 1.0, 'G'),
    TestVector(1000000001, 1.000000001, 'G'),
    # Test progression of small values
    TestVector(0.987654321, 987.654321, 'm'),
    TestVector(0.0987654321, 98.7654321, 'm'),
    TestVector(0.00987654321, 9.87654321, 'm'),
    TestVector(0.000987654321, 987.654321, 'µ'),
    TestVector(0.0000987654321, 98.7654321, 'µ'),
    TestVector(0.00000987654321, 9.87654321, 'µ'),
]  # test_vectors_metric_selected

test_vectors_binary_all_exponents = [
    TestVector(0, 0, '  '),
    TestVector(1024, 1, 'Ki'),
    TestVector(1024*1024, 1, 'Mi'),
    TestVector(1024*1024*1024, 1, 'Gi'),
    TestVector(1024*1024*1024*1024, 1, 'Ti'),
    TestVector(1024*1024*1024*1024*1024, 1, 'Pi'),
    TestVector(1024*1024*1024*1024*1024*1024, 1, 'Ei'),
    TestVector(1024*1024*1024*1024*1024*1024*1024, 1, 'Zi'),
    TestVector(1024*1024*1024*1024*1024*1024*1024*1024, 1, 'Yi'),
    TestVector(1024*1024*1024*1024*1024*1024*1024*1024*1024, 1, 'Ri'),
    TestVector(1024*1024*1024*1024*1024*1024*1024*1024*1024*1024, 1, 'Qi'),
]  # test_vectors_binary_all_exponents

test_vectors_metric_all_exponents = [
    TestVector(1e-24, 1, 'y'),
    TestVector(1e-23, 10, 'y'),
    TestVector(1e-22, 100, 'y'),
    TestVector(1e-21, 1, 'z'),
    TestVector(1e-20, 10, 'z'),
    TestVector(1e-19, 100, 'z'),
    TestVector(1e-18, 1, 'a'),
    TestVector(1e-17, 10, 'a'),
    TestVector(1e-16, 100, 'a'),
    TestVector(1e-15, 1, 'f'),
    TestVector(1e-14, 10, 'f'),
    TestVector(1e-13, 100, 'f'),
    TestVector(1e-12, 1, 'p'),
    TestVector(1e-11, 10, 'p'),
    TestVector(1e-10, 100, 'p'),
    TestVector(1e-9, 1, 'n'),
    TestVector(1e-8, 10, 'n'),
    TestVector(1e-7, 100, 'n'),
    TestVector(1e-6, 1, 'µ'),
    TestVector(1e-5, 10, 'µ'),
    TestVector(1e-4, 100, 'µ'),
    TestVector(1e-3, 1, 'm'),
    TestVector(1e-2, 10, 'm'),
    TestVector(1e-1, 100, 'm'),
    TestVector(1, 1, ' '),
    TestVector(1e1, 10, ' '),
    TestVector(1e2, 100, ' '),
    TestVector(1e3, 1, 'k'),
    TestVector(1e4, 10, 'k'),
    TestVector(1e5, 100, 'k'),
    TestVector(1e6, 1, 'M'),
    TestVector(1e7, 10, 'M'),
    TestVector(1e8, 100, 'M'),
    TestVector(1e9, 1, 'G'),
    TestVector(1e10, 10, 'G'),
    TestVector(1e11, 100, 'G'),
    TestVector(1e12, 1, 'T'),
    TestVector(1e13, 10, 'T'),
    TestVector(1e14, 100, 'T'),
    TestVector(1e15, 1, 'P'),
    TestVector(1e16, 10, 'P'),
    TestVector(1e17, 100, 'P'),
    TestVector(1e18, 1, 'E'),
    TestVector(1e19, 10, 'E'),
    TestVector(1e20, 100, 'E'),
    TestVector(1e21, 1, 'Z'),
    TestVector(1e22, 10, 'Z'),
    TestVector(1e23, 100, 'Z'),
    TestVector(1e24, 1, 'Y'),
    TestVector(1e25, 10, 'Y'),
    TestVector(1e26, 100, 'Y'),
]  # test_vectors_metric_all_exponents


@pytest.mark.parametrize(
    "value, expected_scaled, expected_prefix",
    [(tv.value, tv.expected_scaled, tv.expected_prefix) for tv in test_vectors_binary_selected])
def test_convert_to_prefix_binary(value:float, expected_scaled: float, expected_prefix: str):
    scaled, prefix = convert_to_prefix(value, UnitPrefix.Binary)
    assert math.isclose(scaled, expected_scaled)
    assert prefix == expected_prefix


@pytest.mark.parametrize(
    "value, expected_scaled, expected_prefix",
    [(tv.value, tv.expected_scaled, tv.expected_prefix) for tv in test_vectors_metric_selected])
def test_convert_to_prefix_metric(value:float, expected_scaled: float, expected_prefix: str):
    scaled, prefix = convert_to_prefix(value, UnitPrefix.Metric)
    assert math.isclose(scaled, expected_scaled)
    assert prefix == expected_prefix


@pytest.mark.parametrize(
    "value, expected_scaled, expected_prefix",
    [(tv.value, tv.expected_scaled, tv.expected_prefix) for tv in test_vectors_binary_all_exponents])
def test_convert_to_prefix_all_exponents_binary(value:float, expected_scaled: float, expected_prefix: str):
    scaled, prefix = convert_to_prefix(value, UnitPrefix.Binary)
    assert math.isclose(scaled, expected_scaled)
    assert prefix == expected_prefix


@pytest.mark.parametrize(
    "value, expected_scaled, expected_prefix",
    [(tv.value, tv.expected_scaled, tv.expected_prefix) for tv in test_vectors_metric_all_exponents])
def test_convert_to_prefix_all_exponents_metric(value:float, expected_scaled: float, expected_prefix: str):
    scaled, prefix = convert_to_prefix(value, UnitPrefix.Metric)
    assert math.isclose(scaled, expected_scaled)
    assert prefix == expected_prefix


def test_convert_to_prefix_too_large_binary():
    value = test_vectors_binary_all_exponents[-1].value*1024
    with pytest.raises(ValueError):
        scaled, prefix = convert_to_prefix(value, UnitPrefix.Binary)


def test_convert_to_prefix_too_large_metric():
    value = test_vectors_metric_all_exponents[-1].value*1000
    with pytest.raises(ValueError):
        scaled, prefix = convert_to_prefix(value, UnitPrefix.Metric)


def test_convert_to_prefix_too_small_binary():
    with pytest.raises(ValueError):
        scaled, prefix = convert_to_prefix(0.1, UnitPrefix.Binary)


def test_convert_to_prefix_too_small_binary():
    value = test_vectors_metric_all_exponents[0].value/1000
    with pytest.raises(ValueError):
        scaled, prefix = convert_to_prefix(value, UnitPrefix.Binary)
