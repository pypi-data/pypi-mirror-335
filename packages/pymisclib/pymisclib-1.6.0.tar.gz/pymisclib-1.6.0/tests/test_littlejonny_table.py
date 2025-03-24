#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges
# SPDXID: SPDXRef-test-ringbuffer-py

import unittest

from pymisclib.littlejonny import LineStyle, Table, TableCell


class TestTableDimensions(unittest.TestCase):
    def test_empty_table_dimensions(self):
        table = Table()
        self.assertEqual(0, table.width)
        self.assertEqual(0, table.height)


class TestTableResize(unittest.TestCase):

    def setUp(self):
        self.table = Table(cells=[
            [TableCell('0;0'), TableCell('0;1'), TableCell('0;2'),],
            [TableCell('1;0'), TableCell('1;1'), TableCell('1;2'),],
            [TableCell('2;0'), TableCell('2;1'), TableCell('2;2'),],
        ])

    def table_integrity_check(self, table: Table):
        """Check the content of a table."""
        for r in range(table.height):
            row = table.cells[r]
            for c in range(table.width):
                cell = row[c]
                expect = f'{r};{c}'
                self.assertTrue(cell.content == expect or cell.content == '')

    def test_same_size(self):
        table = self.table
        table.resize(3, 3)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 3)
        self.table_integrity_check(table)

    def test_reduce_to_zero(self):
        table = self.table
        table.resize(0, 0)
        self.assertEqual(table.height, 0)
        self.assertEqual(table.width, 0)
        self.table_integrity_check(table)

    def test_increase_from_zero(self):
        """Test increasing a table with no size."""
        table = Table()
        table.resize(11, 7)
        self.assertEqual(7, table.height)
        self.assertEqual(11, table.width)

    def test_reduce_height(self):
        table = self.table
        table.resize(3, 2)
        self.assertEqual(table.height, 2)
        self.assertEqual(table.width, 3)
        self.table_integrity_check(table)

    def test_reduce_width(self):
        table = self.table
        table.resize(1, 3)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 1)
        self.table_integrity_check(table)

    def test_reduce_width_and_height(self):
        table = self.table
        table.resize(2, 1)
        self.assertEqual(table.height, 1)
        self.assertEqual(table.width, 2)
        self.table_integrity_check(table)

    def test_table_increase_height(self):
        table = self.table
        table.resize(3, 7)
        self.assertEqual(7, table.height)
        self.assertEqual(3, table.width)
        self.table_integrity_check(table)

    def test_cell_at(self):
        table = self.table
        for row in range(table.height):
            for col in range(table.width):
                cell = table.cell_at(col, row)
                self.assertEqual(f'{row};{col}', cell.content)

    def test_cell_at_error(self):
        table = self.table
        with self.assertRaises(IndexError):
            table.cell_at(0, -1)
        with self.assertRaises(IndexError):
            table.cell_at(-1, 0)
        with self.assertRaises(IndexError):
            table.cell_at(0, table.height)
        with self.assertRaises(IndexError):
            table.cell_at(table.width, 0)

    def test_column(self):
        table = self.table
        for col_idx in range(table.width):
            col = table.column(col_idx)
            self.assertEqual(table.height, len(col))
            row_idx = 0
            for cell in col:
                self.assertEqual(f'{row_idx};{col_idx}', cell.content)
                row_idx += 1

    def test_column_error(self):
        """Test invalid arguments to Table.column()."""
        table = self.table
        with self.assertRaises(IndexError):
            table.column(-1)
        with self.assertRaises(IndexError):
            table.column(table.height)

    def test_row(self):
        table = self.table
        for row_idx in range(table.height):
            row = table.row(row_idx)
            self.assertEqual(table.width, len(row))
            col_idx = 0
            for cell in row:
                self.assertEqual(f'{row_idx};{col_idx}', cell.content)
                col_idx += 1

    def test_row_error(self):
        """Test invalid arguments to Table.row()."""
        table = self.table
        with self.assertRaises(IndexError):
            table.row(-1)
        with self.assertRaises(IndexError):
            table.row(table.height)

    def test_resize_error(self):
        table = self.table
        with self.assertRaises(ValueError):
            table.resize(table.width, 0)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 3)
        with self.assertRaises(ValueError):
            table.resize(0, table.height)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 3)
        with self.assertRaises(ValueError):
            table.resize(table.width, -1)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 3)
        with self.assertRaises(ValueError):
            table.resize(-1, table.height)
        self.assertEqual(table.height, 3)
        self.assertEqual(table.width, 3)

#    def test_draw(self):
#        table = self.table
#        lines = table.draw(LineStyle.light)
#        self.assertEqual(1 + table.height * 2, len(lines))


if __name__ == '__main__':
    unittest.main()
