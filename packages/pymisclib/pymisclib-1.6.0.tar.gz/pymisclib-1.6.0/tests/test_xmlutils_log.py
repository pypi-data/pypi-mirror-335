#!/usr/bin/env python3
# vim: fileencoding=utf-8 ts=4
# SPDX-License-Identifier: AGPL-3.0-or-later
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges. All rights reserved.
# SPDXID: SPDXRef-test-xmlutils-log-py

import logging
from xml.etree import ElementTree as ET

import pytest

from pymisclib.xmlutils import log_xml


@pytest.fixture
def logger():
    """Fixture for creating a logger instance."""
    logger = logging.getLogger('pymisclib.xmlutils')
    logger.propagate = True  # see https://stackoverflow.com/a/64424291
    yield logger


@pytest.fixture
def xml_elem():
    """Fixture for creating an XML element instance."""
    elem = ET.Element('elem',
                      attrib={'foo': 'foo', 'bar': 'bar', 'baz': 'yo!'},
                      text='This is a test.')
    ET.SubElement(elem, 'child1')
    child2 = ET.SubElement(elem, 'child2')
    ET.SubElement(child2, 'child2-3',
                  attrib={'a': '1', 'b': '2', 'c': '3'})
    return elem


@pytest.mark.parametrize('indent', [0, 1, 2, 3, 4, 8, 12])
def test_log_xml_indent(caplog, logger, xml_elem, indent: int):
    """Test XML logging with different levels of indent."""
    with caplog.at_level(logging.DEBUG):
        log_xml(logger, xml_elem, level=logging.DEBUG, indent=indent)

    indent_str = ' ' * indent
    lines = [f'{indent_str}{line}'
             for line in ET.tostringlist(xml_elem, encoding='unicode')]
    texts = [r.message for r in caplog.records]
    for l, t in zip(lines, texts):
        assert l == t
