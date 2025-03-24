#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges
# SPDXID: SPDXRef-test-ringbuffer-py
import contextlib
import io
import os
import sys
from pathlib import Path
import random
import tempfile
import unittest

from pymisclib.utilities import std_open


# Create test cases dynamically.
# See https://stackoverflow.com/a/2799009 for how this works.
test_compressed = [
    'file.bz2',
    'file.gz',
    'file.xz',
]
test_uncompressed = [
    'file',  # no suffix
    'file.md',  # markdown suffix
    'file.txt',  # text suffix
    'file.unknown',  # unknown suffix
]

FILE_SIZE = 1024

def generate_random_unicode_string(length: int):
    """Generate a string filled with random unicode code points.

    :param int length: Length of the string to generate.

    :see: https://stackoverflow.com/a/21666621
    """
    # Update this to include code point ranges to be sampled
    include_ranges = [
        ( 0x0021, 0x0021 ),
        ( 0x0023, 0x0026 ),
        ( 0x0028, 0x007E ),
        ( 0x00A1, 0x00AC ),
        ( 0x00AE, 0x00FF ),
        ( 0x0100, 0x017F ),
        ( 0x0180, 0x024F ),
        ( 0x2C60, 0x2C7F ),
        ( 0x16A0, 0x16F0 ),
        ( 0x0370, 0x0377 ),
        ( 0x037A, 0x037E ),
        ( 0x0384, 0x038A ),
        ( 0x038C, 0x038C ),
    ]

    alphabet = [
        chr(code_point) for current_range in include_ranges
            for code_point in range(current_range[0], current_range[1] + 1)
    ]
    return ''.join(random.choice(alphabet) for i in range(length))


class FileTest(unittest.TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        if self.tmp_dir:
            self.tmp_dir.cleanup()
            self.tmp_dir = None


class TestStdOpenCompressed(FileTest):
    pass


class TestStdOpenUncompressed(FileTest):
    pass


class TestStdOpenStdinStdout(FileTest):

    def test_stdin_text(self):
        """Read a text from stdin."""
        text = generate_random_unicode_string(FILE_SIZE)
        old_stdin = sys.stdin
        sys.stdin = io.StringIO(text)
        with std_open('-', 'rt') as f:
            read_text = f.read(FILE_SIZE)
        sys.stdin = old_stdin
        self.assertEqual(text, read_text)

    def test_stdout_text(self):
        text = generate_random_unicode_string(FILE_SIZE)
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            with std_open('-', 'wt') as f:
                f.write(text)
        self.assertEqual(text, stdout.getvalue())


def create_tests_compressed_binary(filename: str):
    """Return a test function for the given test vector (e.g. filename) to
    test compressed binary IO.

    :param str filename: Name of the file to work on. Will be located in a
        temporary directory.
    """
    def test_compressed_binary(self):
        """Test writing to/writing from a compressed file in binary mode.
        Make sure that reading uncompressed fails.
        """
        file_path = Path(self.tmp_dir.name) / filename
        binary = os.urandom(FILE_SIZE)
        with std_open(file_path, 'wb') as f:
            f.write(binary)
        with std_open(file_path, 'rb') as f:
            read_binary = f.read(FILE_SIZE)
            self.assertEqual(read_binary, binary)
        with open(file_path, 'rb') as f:
            read_binary_uncompressed = f.read(FILE_SIZE)
            self.assertNotEqual(read_binary_uncompressed, binary)

    return test_compressed_binary


def create_tests_compressed_text(filename: str):
    """Return a test function for the given test vector (e.g. filename) to
    test compressed text IO.

    :param str filename: Name of the file to work on. Will be located in a
        temporary directory.
    """
    def test_compressed_text(self):
        """Test writing to/writing from a compressed file in text mode.
        Make sure that reading uncompressed fails.
        """
        file_path = Path(self.tmp_dir.name) / filename
        text = generate_random_unicode_string(FILE_SIZE)
        with std_open(file_path, 'wt') as f:
            f.write(text)
        with std_open(file_path, 'rt') as f:
            read_text = f.read(FILE_SIZE)
            self.assertEqual(read_text, text)
        with open(file_path, 'rt') as f:
            try:
                read_text_uncompressed = f.read(FILE_SIZE)
            except UnicodeDecodeError:
                # Reading random binary data as Unicode text is likely to cause
                # an exception, so we'll take that as an indication that the
                # file really is compressed.
                read_text_uncompressed = ''
            self.assertNotEqual(read_text_uncompressed, text)

    return test_compressed_text


def create_tests_uncompressed_binary(filename: str):
    """Return a test function for the given test vector (e.g. filename) to
    test uncompressed binary IO.

    :param str filename: Name of the file to work on. Will be located in a
        temporary directory.
    """
    def test_uncompressed_binary(self):
        """Test writing to/writing from an uncompressed file in binary mode.
        Make sure that reading uncompressed (with plain open()) works.
        """
        file_path = Path(self.tmp_dir.name) / filename
        binary = os.urandom(FILE_SIZE)
        with std_open(file_path, 'wb') as f:
            f.write(binary)
        with std_open(file_path, 'rb') as f:
            read_binary = f.read(FILE_SIZE)
            self.assertEqual(read_binary, binary)
        with open(file_path, 'rb') as f:
            read_binary_uncompressed = f.read(FILE_SIZE)
            self.assertEqual(read_binary_uncompressed, binary)

    return test_uncompressed_binary


def create_tests_uncompressed_text(filename: str):
    """Return a test function for the given test vector (e.g. filename) to
    test uncompressed text IO.

    :param str filename: Name of the file to work on. Will be located in a
        temporary directory.
    """
    def test_uncompressed_text(self):
        """Test writing to a compressed file and then reading from it.
        Make sure that reading uncompressed fails.
        """
        file_path = Path(self.tmp_dir.name) / filename
        text = generate_random_unicode_string(FILE_SIZE)
        with std_open(file_path, 'wt') as f:
            f.write(text)
        with std_open(file_path, 'rt') as f:
            read_text = f.read(FILE_SIZE)
            self.assertEqual(read_text, text)
        with open(file_path, 'rt') as f:
            read_text_uncompressed = f.read(FILE_SIZE)
            self.assertEqual(read_text_uncompressed, text)

    return test_uncompressed_text


for file in test_compressed:
    # Create compressed binary test.
    tst_method = create_tests_compressed_binary(file)
    suffix = Path(file).suffix[1:]
    tst_method.__name__ = (f'test_compressed_binary_{suffix}')
    setattr(TestStdOpenCompressed, tst_method.__name__, tst_method)
    # Create compressed text test.
    tst_method = create_tests_compressed_text(file)
    suffix = Path(file).suffix[1:]
    tst_method.__name__ = (f'test_compressed_text_{suffix}')
    setattr(TestStdOpenCompressed, tst_method.__name__, tst_method)


for file in test_uncompressed:
    # Create uncompressed binary test.
    tst_method = create_tests_uncompressed_binary(file)
    suffix = Path(file).suffix[1:]
    tst_method.__name__ = (f'test_uncompressed_binary_{suffix}')
    setattr(TestStdOpenUncompressed, tst_method.__name__, tst_method)
    # Create uncompressed text test.
    tst_method = create_tests_uncompressed_text(file)
    suffix = Path(file).suffix[1:]
    tst_method.__name__ = (f'test_uncompressed_text_{suffix}')
    setattr(TestStdOpenUncompressed, tst_method.__name__, tst_method)



if __name__ == '__main__':
    unittest.main()
