#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2023 by Christian Dönges
# SPDXID: SPDXRef-test-utilities-iso8601-str-py

import unittest

from pymisclib import utilities

# Create test cases dynamically.
# See https://stackoverflow.com/a/2799009 for how this works.
test_vectors = [
    ['abc', 'abc'],
    ['ABC', 'abc'],
    ['AbCd', 'ab_cd'],
    ['ABCdef', 'ab_cdef'],
    ['aBcde', 'a_bcde'],
    ['aBCDef', 'a_bc_def'],
    ['HTTPResponse', 'http_response'],
    ['getHTTPHeaders', 'get_http_headers'],
    ['abCdeFgh', 'ab_cde_fgh'],
]  # test_vectors

class TestUtilitiesStringToSnakeCase(unittest.TestCase):
    """Test converting a string to snake_case."""
    pass

def create_tests(pair: list[str, str]):
    def do_test_expected(self):
        self.assertEqual(pair[1], utilities.string_to_snake_case(pair[0]))

    return do_test_expected

for index, pair in enumerate(test_vectors):
    test_method = create_tests(pair)
    test_method.__name__ = (f'test_expected_{index}')
    setattr(TestUtilitiesStringToSnakeCase, test_method.__name__, test_method)


if __name__ == '__main__':
    unittest.main()
