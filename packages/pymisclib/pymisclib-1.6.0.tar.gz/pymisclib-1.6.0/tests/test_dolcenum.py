#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-dolcenum-py

import enum

import pytest
from pymisclib.dolcenum import DolcEnumMeta, MissingDocstringError


def test_no_documentation():
    """No documentation at all is allowed."""
    class E(enum.IntFlag, metaclass=DolcEnumMeta):
        b0 = 1
        b1 = 2
        b2 = 4


def test_all_docstrings():
    """Class and all members have a docstring is a good case."""
    class E(enum.IntFlag, metaclass=DolcEnumMeta):
        """Class E docstring."""
        b0 = 1
        """Member E.b0 docstring."""
        b1 = 2
        """Member E.b1 docstring."""
        b2 = 4
        """Member E.b2 docstring."""

    assert E.__doc__ == 'Class E docstring.'
    assert E.b0.__doc__ == 'Member E.b0 docstring.'
    assert E.b1.__doc__ == 'Member E.b1 docstring.'
    assert E.b2.__doc__ == 'Member E.b2 docstring.'


def test_class_docstring_only():
    with pytest.raises(MissingDocstringError):
        class E(enum.IntFlag, metaclass=DolcEnumMeta):
            """Class docstring."""
            b0 = 1
            b1 = 2
            b2 = 4


def test_member_docstring_only():
    """Missing class docstring is a bad case."""
    with pytest.raises(MissingDocstringError):
        class E(enum.IntFlag, metaclass=DolcEnumMeta):
            b0 = 1
            """Member E.b0 docstring."""
            b1 = 2
            """Member E.b1 docstring."""
            b2 = 4
            """Member E.b2 docstring."""


def test_missing_one_docstring():
    with pytest.raises(MissingDocstringError):
        class E(enum.IntFlag, metaclass=DolcEnumMeta):
            """Class E docstring."""
            b0 = 1
            b1 = 2
            """Member E.b1 docstring."""
            b2 = 4
            """Member E.b2 docstring."""

    with pytest.raises(MissingDocstringError):
        class E(enum.IntFlag, metaclass=DolcEnumMeta):
            """Class E docstring."""
            b0 = 1
            """Member E.b0 docstring."""
            b1 = 2
            b2 = 4
            """Member E.b2 docstring."""

    with pytest.raises(MissingDocstringError):
        class E(enum.IntFlag, metaclass=DolcEnumMeta):
            """Class E docstring."""
            b0 = 1
            """Member E.b0 docstring."""
            b1 = 2
            """Member E.b1 docstring."""
            b2 = 4
