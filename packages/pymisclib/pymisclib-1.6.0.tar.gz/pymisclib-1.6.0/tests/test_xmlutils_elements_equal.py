#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-xmlutils-py

from xml.etree import ElementTree as ET

from pymisclib.xmlutils import elements_equal


def test_flat_equal():
    e1 = ET.Element('element')
    e2 = ET.Element('element')
    assert elements_equal(e1, e2)


def test_flat_not_equal():
    e1 = ET.Element('element_one')
    e2 = ET.Element('element_two')
    assert not elements_equal(e1, e2)


def test_flat_with_attributes_equal():
    e1 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2'})
    e2 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2'})
    assert elements_equal(e1, e2)

    e3 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2'})
    e4 = ET.Element('element',
                    attrib={'b': 'val2', 'a': 'val1'})
    assert elements_equal(e3, e4)


    e3 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2',
        'c': 'val3'})
    e4 = ET.Element('element',
                    attrib={'c': 'val3', 'b': 'val2',
        'a': 'val1'})
    assert elements_equal(e3, e4)


def test_flat_with_attributes_not_equal():
    """Compare flat elements with different attributes."""
    # Attribute value differs.
    e1 = ET.Element('element',
                    attrib={'a': 'val1'})
    e2 = ET.Element('element',
                    attrib={'a': 'val2'})
    assert not elements_equal(e1, e2)

    # Number of attributes differs.
    e3 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2'})
    assert not elements_equal(e1, e3)

    # Wrong value type.
    e4 = ET.Element('element',
                    attrib={'a': 'val1', 'b': '2'})
    e5 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 2})
    assert not elements_equal(e4, e5)


def test_flat_with_text_equal():
    """Compare flat elements with the same text."""
    e1 = ET.Element('element', text='text1')
    e2 = ET.Element('element', text='text1')
    assert elements_equal(e1, e2)


def test_flat_with_text_not_equal():
    """Compare flat elements with different text."""
    # Different text
    e1 = ET.Element('element', text='text1')
    e2 = ET.Element('element', text='text2')
    assert not elements_equal(e1, e2)

    # Case is significant.
    e3 = ET.Element('element', text='Text1')
    assert not elements_equal(e1, e3)
    e4 = ET.Element('element', text='teXt1')
    assert not elements_equal(e1, e4)


def test_flat_with_tail_equal():
    """Compare flat elements with the same tail."""
    e1 = ET.Element('element', tail='tail1')
    e2 = ET.Element('element', tail='tail1')
    assert elements_equal(e1, e2)

    # Non-ASCII characters.
    e3 = ET.Element('element', tail='This is a Ⲧäïл.')
    e4 = ET.Element('element', tail='This is a Ⲧäïл.')
    assert elements_equal(e3, e4)


def test_flat_with_tail_not_equal():
    """Compare flat elements with different tail."""
    e1 = ET.Element('element', tail='tail1')
    e2 = ET.Element('element', tail='tail2')
    assert not elements_equal(e1, e2)

    # Case is significant.
    e3 = ET.Element('element', tail='Tail1')
    assert not elements_equal(e1, e3)
    e4 = ET.Element('element', tail='taIL1')
    assert not elements_equal(e1, e4)

    # Whitespace is significant.
    e5 = ET.Element('element', tail='This is a tail.')
    e6 = ET.Element('element', tail='This  is a tail.')
    assert not elements_equal(e5, e6)

    # Non-ASCII characters.
    e7 = ET.Element('element', tail='This is a Täïл.')
    e8 = ET.Element('element', tail='This is a Ⲧäïл.')
    assert not elements_equal(e7, e8)


def test_flat_all_equal():
    """Compare flat elements with attributes, tail, and text."""
    e1 = ET.Element('element',
                    attrib={'a': 'val1', 'b': 'val2'},
                    text='text1',
                    tail='tail1')
    e2 = ET.Element('element',
                    attrib={'b': 'val2', 'a': 'val1'},
                    text='text1',
                    tail='tail1')
    assert elements_equal(e1, e2)


def test_children_equal_1():
    """Compare elements with identical one child."""
    e1 = ET.Element('element')
    c1 = ET.SubElement(e1, 'child',
                       attrib={'a': 'val1', 'b': 'val2'},
                       tail='tail1',
                       text='text1')
    e2 = ET.Element('element')
    c2 = ET.SubElement(e2, 'child',
                       attrib={'b': 'val2', 'a': 'val1'},
                       tail='tail1',
                       text='text1')
    assert elements_equal(e1, e2)


def test_children_order_equal_2():
    """Compare elements with identical two children."""
    e1 = ET.Element('parent')
    c11 = ET.SubElement(e1, 'child',
                       attrib={'a': 'val1', 'b': 'val2'},
                       tail='tail1',
                       text='text1')
    c12 = ET.SubElement(e1, 'child',
                       attrib={'c': 'val1', 'd': 'val2'},
                       tail='tail2',
                       text='text2')
    e2 = ET.Element('parent')
    c21 = ET.SubElement(e2, 'child',
                        attrib={'b': 'val2', 'a': 'val1'},
                        tail='tail1',
                        text='text1')
    c22 = ET.SubElement(e2, 'child',
                        attrib={'d': 'val2', 'c': 'val1'},
                        tail='tail2',
                        text='text2'),
    assert elements_equal(e1, e2)


def test_children_order_not_equal_2():
    """Compare elements with identical two children in wrong order."""
    e1 = ET.Element('parent')
    c11 = ET.SubElement(e1, 'child',
                       attrib={'a': 'val1', 'b': 'val2'},
                       tail='tail1',
                       text='text1')
    c12 = ET.SubElement(e1, 'child',
                       attrib={'c': 'val1', 'd': 'val2'},
                       tail='tail2',
                       text='text2')
    e2 = ET.Element('parent')
    c21 = ET.SubElement(e2, 'child',
                        attrib={'d': 'val2', 'c': 'val1'},
                        tail='tail2',
                        text='text2'),
    c22 = ET.SubElement(e2, 'child',
                        attrib={'b': 'val2', 'a': 'val1'},
                        tail='tail1',
                        text='text1')
    assert not elements_equal(e1, e2)

