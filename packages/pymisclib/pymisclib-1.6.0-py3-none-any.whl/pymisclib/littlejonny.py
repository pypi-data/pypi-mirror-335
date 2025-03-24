#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2022, 2023, 2025 by Christian Dönges
# SPDXID: SPDXRef-littlejonny-py
"""Format output to a text table.

   In case you have been wondering, the name is a reference to
   https://xkcd.com/327/.


.. deprecated:: 1.6.0 Will be removed in 2.0.

"""

# Postpone type hint evaluation until after the entire class has been parsed.
# This was to become standard in 3.10 but will probably never be.
# @see https://stackoverflow.com/a/33533514
# @see https://mail.python.org/archives/list/python-dev@python.org/thread/CLVXXPQ2T2LQ5MP2Y53VVQFCXYWQJHKZ/
from __future__ import annotations


import enum
import logging
from dataclasses import dataclass, field
from typing import Any

from pymisclib.ansiterminal import AnsiControl, BgColor, FgColor, TextStyle
from pymisclib.unicodechars import UC


# Box drawing characters.
# The beauty of Namespace makes it possible to access a character like so:
# box_drawings.light.horizontal.
box_drawings = UC.box_drawings

# Type definition: a Text is a collection of lines, each of which is a string.
Text = list[str]
"""Type definition: a Text is a collection of lines, each of which is a string.

    The lines are organized by row, so the first string in the list is the first text line.
"""


@enum.unique
class LineStyle(enum.Enum):
    """Rendering style for lines."""
    double = box_drawings.double
    """Double line style ║."""
    light = box_drawings.light
    """Light single line style │."""
    heavy = box_drawings.heavy
    """Heavy single line style ┃."""


@enum.unique
class OutputFormat(enum.Enum):
    """Format for rendering the output."""
    ANSI = enum.auto()
    """Render for an ANSI terminal."""
    TEXT = enum.auto()
    """Render as plain text."""


@dataclass
class Point:
    """Coordinate in column (x) / row (y) space."""
    column: int = 1
    row: int = 1

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return f'({self.column};{self.row})'


@dataclass
class Box:
    """A box consisting of a frame with content.

        Constructor arguments:
            :param int origin_column: Top left corner column.
            :param int origin_row: Top left corner row.
            :param int width: Width in columns.
            :param int height: Height in rows.
            :param LineStyle line_style: Border line style.
            :param str border_style: Border color and font style expressed as ANSI format codes.
            :param str text_style: Content text color and font style expressed as ANSI format codes.
    """
    origin_column: int = 1  # starting x-coordinate
    """X-coordinate of the upper left corner of the box."""
    origin_row: int = 1  # starting y coordinate
    """Y-coordinate of the upper left corner of the box."""
    width: int = 40
    """Width of the box in columns."""
    height: int = 20
    """Height of the box in rows."""
    line_style: LineStyle = LineStyle.light
    """Style of the border characters."""
    border_style: str = FgColor.Black.value + BgColor.White.value
    """Rendering style (color and font style) of the border."""
    text_style: str = FgColor.Blue.value + BgColor.BrightYellow.value + TextStyle.Bold.value
    """Text style (color and font) of the content."""
    _text: Text = field(default_factory=list)

    @classmethod
    def make_from_points(cls, top_left: Point,
                         bottom_right: Point,
                         line_style: LineStyle = LineStyle.light) -> Box:
        """Create a new Box instance with the given top left and bottom right
        points.

        :param Point top_left: starting point in the upper left corner.
        :param Point bottom_right: ending point (inclusive) in the lower right
            corner.
        :param LineStyle line_style: Style to use when rendering the box.
        :return: An initialized instance.
        :rtype Box:
        """
        if top_left.column < 1:
            raise ValueError('left column too small')
        if top_left.row < 1:
            raise ValueError('top row too small')
        if bottom_right.column <= top_left.column:
            raise ValueError('right column too small')
        if bottom_right.row <= top_left.row:
            raise ValueError('bottom column too small')
        width = bottom_right.column - top_left.column
        height = bottom_right.row - top_left.row
        return Box(top_left.row, top_left.column, width, height, line_style)

    def flow_text(self, text: str, truncate: bool = True):
        """Flow the given text in to the current box.

        :param str text: Text to flow into the box.
        :param bool truncate: If False, raise an exception if text won't fit into
            the box. If True, truncate the text.
        """
        self.text = flow_text(text, self.width, self.height, truncate)


    @property
    def text(self) -> Text:
        """Text contained in the box."""
        return self._text

    @text.setter
    def text(self, text: Text|str, truncate: bool = True):
        """Set the text contained in the box.

        If the text is a Text, it will simply be fit into the box. If it is a
        string, it will be flowed into the box.

        :param str|Text text: Text to flow into the box.
        :param bool truncate: If False, raise an exception if text won't fit.
        :raise ValueError: Raised if the text won't fit into the box and
            truncate is set to False.
        """
        self._text = []
        if isinstance(text, str):
            text = flow_text(text, self.width, self.height, truncate)
        if len(text) > self.height:
            if truncate:
                edited_text = text[:self.height]
            else:
                raise ValueError('too many lines')
        else:
            edited_text = text
        for line in edited_text:
            if len(line) > self.width:
                if truncate:
                    line = line[:self.width]
                else:
                    ValueError('line too wide')
            else:
                line = line + ' ' * (self.width - len(line))
            self._text.append(line)

    def render(self, output_format: OutputFormat) -> Text:
        """Render the box in the given output_format.

        :param OutputFormat output_format: Rendering format.
        :return: A list of lines rendering the instance.
        :rtype Text:
        """
        if output_format == OutputFormat.ANSI:
            return self._render_ansi()
        elif output_format == OutputFormat.TEXT:
            return self._render_text()
        raise ValueError('unknown output output_format')

    def _render_ansi(self) -> Text:
        """Render the instance on an ANSI terminal."""
        lines = []
        if self.origin_column > 1:
            prefix = AnsiControl.move_cursor_forward(self.origin_column - 1)
        else:
            prefix = ''
        box = self.line_style.value
        s = self.border_style + box.down_and_right + box.horizontal * self.width + \
            box.down_and_left + TextStyle.Reset.value
        if self.origin_column > 1 or self.origin_row > 1:
            s = AnsiControl.move_cursor_to(self.origin_column, self.origin_row) + s
        else:
            s = prefix + s
        lines.append(s)
        s = prefix + self.border_style + box.vertical + \
            self.text_style + (' ' * self.width) + TextStyle.Reset.value + \
            self.border_style + box.vertical + TextStyle.Reset.value
        for i in range(self.height):
            if i < len(self._text):
                lines.append(prefix + self.border_style + box.vertical +
                             self.text_style + self._text[i] + TextStyle.Reset.value +
                             self.border_style + box.vertical + TextStyle.Reset.value)
            else:
                lines.append(s)
        s = prefix + self.border_style + box.up_and_right + \
            box.horizontal * self.width + box.up_and_left + TextStyle.Reset.value
        lines.append(s)

        return lines

    def _render_text(self) -> Text:
        """Render the instance on dumb terminal (e.g. as plain text).

        The origin column and row are created using spaces and blank lines.

        :return: A list of lines, each of which is a string that contains no
            formatting characters.
        :rtype list[str]:
        """
        lines = []
        if self.origin_row > 1:
            for i in range(self.origin_row - 1):
                lines.append('')
        prefix = ' ' * (self.origin_column - 1)
        box = self.line_style.value
        s = prefix + box.down_and_right + box.horizontal * self.width + box.down_and_left
        lines.append(s)
        s = prefix + box.vertical + ' ' * self.width + box.vertical
        for i in range(self.height):
            if i < len(self._text):
                lines.append(prefix + box.vertical + self._text[i] + box.vertical)
            else:
                lines.append(s)
        s = prefix + box.up_and_right + box.horizontal * self.width + box.up_and_left
        lines.append(s)

        return lines


@dataclass
class ColumnTable:
    """Table with data arranged by column.

    .. deprecated:: 2.0.0
    """
    _headings: list[str] = field(default_factory=list)  # row or column heading
    _formats: list[str] = field(default_factory=list)  # cell formats
    _cells: list[list[Any]] = field(default_factory=list)  # column[row]
    _num_columns: int = 0
    _num_rows: int = 0

    @property
    def cell_formats(self) -> list[str]:
        """Return cell formats by columns."""
        return self._formats

    @property
    def headings(self) -> list[str]:
        """Return headings by column."""
        return self._headings

    @property
    def num_columns(self):
        """Number of columns in the table."""
        return self._num_columns

    @property
    def num_rows(self):
        """Number of rows in the table."""
        return self._num_rows

    def set_table(self,
                  headings: list[str],
                  cell_formats: list[str],
                  cells: list[list[str]]):
        """Set the content of the table with cells specified by column.

            :param list[str] headings: List of headings.
            :param list[str] cell_formats: List of cell formats for each column.
                The formats use the same format-language as Python format strings.
            :param list[str] cells: Matrix of cell contents, specified column[row].

            Example
            ---------

            .. code-block:: python

                ct2 = ColumnTable()
                ct2.set_table(
                    headings=['First', 'Second', 'Third', 'Fourth'],
                    cell_formats=['3d', '08x', 's', '>s'],
                    cells=[[1, 2, 12, 123, 1000],
                           [0x12345678, 0xffffee01, -1, 0, 23],
                           ['abc def geh', '12345', 'minus one', 'zero', 'First'],
                           ['this is a sample text', 'Short', 'negative hex number',
                            'Zero hexadecimal number', 'The first column is too large.']]
                )
                print_lines(ct2.draw(LineStyle.light))

            Output::

                ┌───────┬──────────┬─────────────┬────────────────────────────────┐
                │ First │ Second   │ Third       │ Fourth                         │
                ├───────┼──────────┼─────────────┼────────────────────────────────┤
                │   1   │ 12345678 │ abc def geh │ this is a sample text          │
                │   2   │ ffffee01 │ 12345       │ Short                          │
                │  12   │ -0000001 │ minus one   │ negative hex number            │
                │ 123   │ 00000000 │ zero        │ Zero hexadecimal number        │
                │ 1000  │ 00000017 │ First       │ The first column is too large. │
                └───────┴──────────┴─────────────┴────────────────────────────────┘
        """
        if len(headings) != len(cell_formats):
            raise ValueError('number columns in headings and formats do not match')
        if len(headings) != len(cells):
            raise ValueError('number of columns in headings and cells do not match')
        self._num_columns = len(headings)
        self._num_rows = len(cells[0])
        self._headings = headings
        self._formats = cell_formats
        self._cells = cells

    def set_table_transposed(self,
                             headings: list[str],
                             cell_formats: list[str],
                             cells: list[list[str]]):
        """Set the content of the table with cells specified by row.

            :param list[str] headings: List of headings.
            :param list[str] cell_formats: List of cell formats for each column.
            :param list[str] cells: Matrix of cell contents, specified row[column].

            Example
            ---------

            .. code-block:: python

                ct1 = ColumnTable()
                ct1.set_table_transposed(
                    headings=['First', 'Second', 'Third', 'Fourth'],
                    cell_formats=['3d', '08x', 's', '>s'],
                    cells=[[1, 0x12345678, 'abc def geh', 'this is a sample text'],
                           [2, 0xffffee01, '12345', 'Short'],
                           [12, -1, 'minus one', 'negative hex number'],
                           [123, 0, 'zero', 'Zero hexadecimal number'],
                           [1000, 23, 'First', 'The first column is too large.']]
                )
                print_lines(ct1.draw(LineStyle.light))

            Output::

                ┌───────┬──────────┬─────────────┬────────────────────────────────┐
                │ First │ Second   │ Third       │ Fourth                         │
                ├───────┼──────────┼─────────────┼────────────────────────────────┤
                │   1   │ 12345678 │ abc def geh │ this is a sample text          │
                │   2   │ ffffee01 │ 12345       │ Short                          │
                │  12   │ -0000001 │ minus one   │ negative hex number            │
                │ 123   │ 00000000 │ zero        │ Zero hexadecimal number        │
                │ 1000  │ 00000017 │ First       │ The first column is too large. │
                └───────┴──────────┴─────────────┴────────────────────────────────┘
        """
        transposed_cells = [list(x) for x in zip(*cells)]
        self.set_table(headings, cell_formats, transposed_cells)

    def draw(self, style: LineStyle) -> Text:
        """Render the table to a list of lines.

            :param LineStyle style: The line style to use for the table.
            :rtype Text:
            :return: A list of rows which make up the rendered table.
        """
        formatted_cells = []
        column_widths = []
        for c in range(self.num_columns):
            column_width = len(self._headings[c])
            column_data = self._cells[c]
            fmt = self._formats[c]
            formatted_column = []
            for cell in column_data:
                formatted_cell = f'{cell:{fmt}}'
                formatted_column.append(formatted_cell)
                column_width = max(column_width,  len(formatted_cell))
            formatted_cells.append(formatted_column)
            column_widths.append(column_width)

        box = style.value
        lines = []
        first = True
        s = ''
        for c in range(self.num_columns):
            column_width = column_widths[c]
            if first:
                s = box.down_and_right + box.horizontal * (column_width + 2)
                first = False
            else:
                s += box.down_and_horizontal + box.horizontal * (column_width + 2)
        s += box.down_and_left
        lines.append(s)

        s = ''
        for c in range(self.num_columns):
            column_width = column_widths[c]
            s += box.vertical + f' {self._headings[c]:{column_width}s} '
        s += box.vertical
        lines.append(s)

        first = True
        s = ''
        for c in range(self.num_columns):
            column_width = column_widths[c]
            if first:
                s = box.vertical_and_right + box.horizontal * (column_width + 2)
                first = False
            else:
                s += box.vertical_and_horizontal + box.horizontal * (column_width + 2)
        s += box.vertical_and_left
        lines.append(s)

        for r in range(self.num_rows):
            s = ''
            for c in range(self.num_columns):
                column_width = column_widths[c]
                s += box.vertical + f' {formatted_cells[c][r]:{column_width}s} '
            s += box.vertical
            lines.append(s)

        first = True
        s = ''
        for c in range(self.num_columns):
            column_width = column_widths[c]
            if first:
                s = box.up_and_right + box.horizontal * (column_width + 2)
                first = False
            else:
                s += box.up_and_horizontal + box.horizontal * (column_width + 2)
        s += box.up_and_left
        lines.append(s)

        return lines


@enum.unique
class Alignment(enum.Enum):
    """Content alignment within a cell."""
    Center = '^'
    """Align content in the center of the cell."""
    Left = '<'
    """Align content to the left of the cell."""
    Right = '>'
    """Align content to the right of the cell."""


@dataclass
class CellStyle:
    """Styling to use for the cell."""
    heading_style: str = TextStyle.Bold.value
    """Heading cell content style as a string of ANSI escape codes.
    Default is **bold**.
    """
    plain_style: str = ''
    """Plain cell content style as a string of ANSI escape codes.
    Default is plain.
    """


@dataclass
class TableCell:
    """A single cell of a table.

    Constructor arguments:
        :param Any content: Content of the cell. Usually a string or number.
        :param str fmt: f-string `format_spec` to format the content.
        :param bool is_heading: True if the cell is a heading cell.
        :param Alignment alignment: Alignment of the formatted content in the
            cell.
        :param CellStyle style: Style of the rendered content.
    """
    content: Any = ''  # Content that is rendered.
    fmt: str = 's'  # Format string to render the content.
    is_heading: bool = False  # True to render as heading.
    alignment: Alignment = Alignment.Right
    style: CellStyle = None
    join_right: bool = False  # Join with the cell to the right.
    join_bottom: bool = False  # Join with the cell below.

    def render(self,
               output_format: OutputFormat = OutputFormat.TEXT,
               width: int = 0) -> Text:
        """Render the box in the given output_format.

        :param OutputFormat output_format: Rendering format.
        :param int width: Width of the cell. If zero, the width is unconstrained
            and the content will not be aligned.
        :return: A list of lines representing the instance.
        :rtype: Text
        """
        if output_format == OutputFormat.ANSI:
            return self._render_ansi(width)
        elif output_format == OutputFormat.TEXT:
            return self._render_text(width)
        raise ValueError('unknown output output_format')

    def _render_ansi(self, width: int) -> str:
        """Render the content as a text string with ANSI formatting.

        :param int width: Width of the cell.
        :return: ANSI representation of the cell.
        :rtype: str
        """
        s = self._render_text(width)
        if self.style is not None:
            if self.is_heading:
                s = self.style.heading_style + s + TextStyle.Reset.value
            else:
                s = self.style.plain_style + s + TextStyle.Reset.value
        return s

    def _render_text(self, width: int) -> str:
        """Render the content as a text string.

        :param int width: Width of the cell.
        :return: Text representation of the cell.
        :rtype: str
        """
        try:
            formatted_str = f'{self.content:{self.fmt}}'
        except ValueError:
            formatted_str = str(self.content)

        if width:
            aligned_str = f'{formatted_str:{self.alignment.value}{width}s}'[:width]
        else:
            aligned_str = formatted_str
        return aligned_str

    def set(self, value: Any,
            fmt: str = '%s',
            justify: Alignment = Alignment.Right,
            is_heading: bool = False):
        """Set the value of the content and the format string for rendering.

        :param Any value: Content of the cell.
        :param str fmt: Format string for the cell value. Uses f-string syntax.
        :param Alignment justify: Cell justification after formatting.
        :param bool is_heading: True if cell gets heading formatting, False otherwise.
        """
        self.content = value
        self.fmt = fmt
        self.alignment = justify
        self.is_heading = is_heading


@dataclass
class Table:
    """Table made up of a rectangle of :py:class:`TableCell` instances.

    Constructor arguments:
        :param list[list[TableCell]] | None cells: Two-dimensional list of
            :py:class:`TableCell` instances making up the table. The cells are
            organized by row and column (.e.g. `cells[row][column]`).
        :param logging.Logger logger: Logger instance for diagnostics.
        :param CellsStyle default_style: All new cells start with this style.
    """
    cells: list[list[TableCell]] | None = None
    """Cells, ordered by row and column, e.g. cells[row][column]."""
    logger: logging.Logger = logging.getLogger(__name__)
    """Logger instance for diagnostics."""
    default_style: CellStyle = field(default_factory=lambda: CellStyle())
    """Style all cells using this style unless specified otherwise."""
    column_widths: list[int] = field(default_factory=list)  # 0 to auto-size

    def __post_init__(self):
        """Initializations performed after the constructor was called."""
        if len(self.column_widths) == 0:
            self.column_widths = [0] * self.width
        if self.width != len(self.column_widths):
            raise ValueError(f'Table has {self.width} columns, '
                             f'{len(self.column_widths)} column widths given.')

    @property
    def height(self) -> int:
        """Number of rows in the table."""
        if self.cells is None:
            return 0
        return len(self.cells)

    @property
    def width(self) -> int:
        """Number of columns in the table."""
        if self.cells is None:
            return 0
        return len(self.cells[0])

    def cell_at(self, column: int, row: int) -> TableCell:
        """Return the cell at the given location.

        :param int column: Column number of the cell.
        :param int row: Row number of the cell.
        :return: Cell of the table at the given location.
        :rtype: TableCell
        :raises IndexError: Row or column was invalid.
        """
        if column < 0 or column >= self.width:
            raise IndexError('invalid column number')
        if row < 0 or row >= self.height:
            raise IndexError('invalid row number')
        return self.cells[row][column]

    def column(self, column_idx: int) -> list[TableCell]:
        """Return the specified column of the table.

        :param int column_idx: Column index [0..table.width[.
        :return: List of cells in the column ordered by row.
        :rtype list[TableCell]:
        :raises IndexError: Column was invalid
        """
        if column_idx < 0 or column_idx >= self.height:
            raise IndexError(f'invalid column number {column_idx}')
        column = [r[column_idx] for r in self.cells]
        return column

    def column_width(self, column_idx: int) -> int:
        """Return the configured width of the specified column.

        :param int column_idx: Column index [0..table.width[.
        :return: Configured width of the column, or 0 to auto-size.
        :rtype: int
        :raises IndexError: Column was invalid
        """
        if column_idx < 0 or column_idx >= self.height:
            raise IndexError(f'invalid column number {column_idx}')
        return self.column_widths[column_idx]

    def populate(self, content: list[list[Any]],
                 column_formats: list[str],
                 column_alignment: list[str] | None = None):
        """Resize and populate a table with the given content.

        """
        self.logger.debug('%s.populate(%d, %d)', len(content), len(column_formats))
        # Check arguments for consistency.
        num_columns = len(column_formats)
        if num_columns == 0:
            raise IndexError('no columns')
        if len(content) == 0:
            raise IndexError('no rows')
        for row in content:
            if len(row) != num_columns:
                self.logger.error('Expected %d columns, found %d.', num_columns, len(row))
                raise IndexError('content wrong number of columns')
        if column_alignment is None:
            column_alignment = [Alignment.Left] * num_columns
        elif len(column_alignment) != num_columns:
            self.logger.error('Expected %d columns, found column_alignment:%d.', num_columns, len(column_alignment))
            raise IndexError('column_alignment wrong number of columns')
        self.resize(num_columns, len(content))
        for row_idx, row in enumerate(content):
            for column_idx, cell_content in enumerate(row):
                self.cells[row_idx][column_idx].set(cell_content,
                                                    column_formats[column_idx],
                                                    column_alignment[column_idx])
        self.column_widths = [0] * num_columns

    def render(self,
               output_format: OutputFormat = OutputFormat.TEXT,
               line_style: LineStyle = LineStyle.light) -> Text:
        """Render the table in the given format to a list of strings.

        :param OutputFormat output_format: Format to render to.
        :param LineStyle line_style: Style used to render cell borders.
        :return: Rendered repsentation of the instance.
        :rtype: Text
        """
        self.logger.debug('%s.render(%s, %s)', self.__class__.__name__,
                          output_format.name, line_style.name)
        lines = []
        column_widths = [0] * self.width  # width in characters of each column
        for column_idx in range(self.width):
            tcw = self.column_widths[column_idx]
            if tcw > 0:
                # Use configured width.
                column_widths[column_idx] = tcw
            else:
                # Use maximum width of any cell in the column.
                col = self.column(column_idx)
                for cell in col:
                    rc = cell.render(output_format=OutputFormat.TEXT)
                    column_widths[column_idx] = max(column_widths[column_idx], len(rc))

        bs = line_style.value
        previous_row = None
        for row_idx in range(self.height):
            row = self.cells[row_idx]
            # Render the top cell border.
            s = ''
            joining_right = False
            joining_previous_right = False
            for column_idx in range(self.width):
                column_width = column_widths[column_idx]
                if row_idx == 0:
                    if column_idx == 0:
                        s = bs.down_and_right + bs.horizontal * (column_width + 2)
                    else:
                        if joining_right:
                            s += bs.horizontal * (column_width + 3)
                        else:
                            s += bs.down_and_horizontal + bs.horizontal * (column_width + 2)
                else:
                    if column_idx == 0:
                        s = bs.vertical_and_right + bs.horizontal * (column_width + 2)
                    else:
                        if joining_right:
                            if joining_previous_right:
                                s += bs.horizontal * (column_width + 3)
                            else:
                                s += bs.up_and_horizontal + bs.horizontal * (column_width + 2)
                        else:
                            if joining_previous_right:
                                s += bs.down_and_horizontal + bs.horizontal * (column_width + 2)
                            else:
                                s += bs.vertical_and_horizontal + bs.horizontal * (column_width + 2)
                cell = row[column_idx]
                joining_right = cell.join_right
                if previous_row:
                    joining_previous_right = previous_row[column_idx].join_right
            if row_idx == 0:
                s+= bs.down_and_left
            else:
                s += bs.vertical_and_left
            lines.append(s)

            # Render the cell side borders and content.
            s = ''
            joining_right = False
            for column_idx in range(self.width):
                cell = row[column_idx]
                if joining_right:
                    # This is the nth cell of the join.
                    column_width += column_widths[column_idx] + 3
                else:
                    column_width = column_widths[column_idx]
                    render_cell = cell
                if cell.join_right:
                    # Defer rendering until we reach the end of the joined section.
                    joining_right = True
                    continue
                rc = render_cell.render(output_format, width=column_width)
                s += bs.vertical + f' {rc} '
                joining_right = False
            s += bs.vertical
            lines.append(s)
            previous_row = row

        # Render the bottom table border.
        s = ''
        joining_right = False
        for column_idx in range(self.width):
            column_width = column_widths[column_idx]
            if column_idx == 0:
                s = bs.up_and_right + bs.horizontal * (column_width + 2)
            else:
                if joining_right:
                    s += bs.horizontal * (column_width + 3)
                else:
                    s += bs.up_and_horizontal + bs.horizontal * (column_width + 2)
            cell = row[column_idx]
            joining_right = cell.join_right
        s += bs.up_and_left
        lines.append(s)
        return lines


    def resize(self, width: int, height: int):
        """Resize the table to the given width and height.

        :param int width: Number of columns in the table.
        :param int height: Number of rows in the table.
        """
        self.logger.debug('%s.resize(%d, %d)', self.__class__.__name__, width, height)

        # Error checking.
        if width < 0:
            raise ValueError('width must be non-negative')
        if height < 0:
            raise ValueError('height must be non-negative')
        if width == 0 or height == 0:
            if width != height:
                raise ValueError('width and height must both be zero')
            self.cells = None
            return

        if height < self.height:
            self.logger.debug('Reduce number of rows from %d to %d.', self.height, height)
            self.cells = self.cells[:height]
        else:
            num_rows_to_add = height - self.height
            if num_rows_to_add > 0:
                self.logger.debug('Extend number of rows from %d to %d.', self.height, height)
                num_columns = self.width
                if self.cells is None:
                    self.cells = []
                for i in range(num_rows_to_add):
                    row = []
                    for j in range(num_columns):
                        row.append(TableCell(style=self.default_style))
                    self.cells.append(row)
        if width < self.width:
            self.logger.debug('Reduce number of columns from %d to %d.', self.width, width)
            for r in range(self.height):
                self.cells[r] = self.cells[r][:width]
            self.column_widths = self.column_widths[:width]
        else:
            num_columns_to_add = width - self.width
            if num_columns_to_add > 0:
                self.logger.debug('Extend number of columns from %d to %d.', self.width, width)
                for r in range(self.height):
                    for c in range(num_columns_to_add):
                        self.cells[r].append(TableCell(style=self.default_style))
                self.column_widths += [0] * num_columns_to_add

    def row(self, row_idx: int) -> list[TableCell]:
        """Return the specified row of the table.

        :param int row_idx: Row index [0..table.height[.
        :return: List of cells in the row, ordered by column.
        :rtype list[TableCell]:
        :raises IndexError: Column was invalid
        """
        if row_idx < 0 or row_idx >= self.height:
            raise IndexError(f'invalid row number {row_idx}')
        row = self.cells[row_idx]
        return row

    def set_column_width(self, column_idx: int, width: int):
        """Set the width in characters of the given column..

        :param int column_idx: Column index [0..table.width[.
        :param int width: Width in characters or 0 to auto-size.
        :raises IndexError: Column was invalid.
        :raises ValueError: Width was less than zero.
        """
        if column_idx < 0 or column_idx >= self.height:
            raise IndexError(f'invalid column number {column_idx}')
        if width < 0:
            raise ValueError(f'invalid width {width}')
        self.column_widths[column_idx] = width


def draw_box(x, y, style) -> Text:
    """Construct a box of size x * y with style."""
    box = style.value

    lines = []
    s = box.down_and_right + box.horizontal * x + box.down_and_left
    lines.append(s)
    s = box.vertical + ' ' * x + box.vertical
    for i in range(y):
        lines.append(s)
    s = box.up_and_right + box.horizontal * x + box.up_and_left
    lines.append(s)

    return lines


def flow_text(text: str,
              width: int = 0,
              height: int = 0,
              truncate: bool = True) -> Text:
    """Flow the given text in to the given space.

    :param str text: Text to flow into the box.
    :param int width: Number of characters in a line to flow text into.
    :param int height: Number of lines to flow text into.
    :param bool truncate: If False, raise an exception if text won't fit into
        the box. If True, truncate the text.
    :rtype: Text
    :return: Flowed text, one string per line, from top to bottom.
    """
    if width < 0:
        raise ValueError('width must be positive or zero')
    if height < 0:
        raise ValueError('height must be positive or zero')
    if width == 0:
        # No width constraint means we can go as wide as we want.
        return [text]
    lines: list[str] = []
    start_offset = 0
    max_offset = len(text) - 1
    while start_offset < max_offset:
        end_of_line_offset = min(start_offset + width, max_offset)
        skip_space = 1
        if start_offset + width < max_offset:
            end_of_line_offset = start_offset + width
            wrap_offset = text.rfind(' ', start_offset, end_of_line_offset)
        else:
            end_of_line_offset = max_offset
            wrap_offset = end_of_line_offset + 1
        if wrap_offset < 0:
            # No space found to wrap line.
            if truncate:
                wrap_offset = end_of_line_offset
                skip_space = 0
            else:
                raise ValueError('unable to wrap text')
        line = text[start_offset:wrap_offset]
        lines.append(line)
        start_offset = wrap_offset + skip_space
    if height != 0 and len(lines) > height:
        if truncate:
            lines = lines[:height]
        else:
            ValueError(f'too many lines of text: {len(lines)} > {height}')
    return lines


def print_lines(lines: Text):
    """Print lines stored as a list of strings to stdout."""
    for line in lines:
        print(line)


def demo_table_simple():
    """Demonstrate the use of the Table class."""
    print('Demonstrate simple use of the Table class.')
    cell_alignment = [Alignment.Left,
                    Alignment.Center,
                    Alignment.Right,
                    Alignment.Center,
                    Alignment.Left]
    cell_formats=['3d', '08x', 's', '>s', '<s']
    cell_contents=[
       [j.name for j in cell_alignment],
       [1, 2, 12, 123, 1000],
       [0x12345678, 0xffffee01, -1, 0, 23],
       ['abc def geh', 12345, 'minus one', 'zero', 'First'],
       ['this is a sample text', -5, 'negative hex number',
        'Zero hexadecimal number', 'The first column is too large.'],
       [97.2, 123, '***', '***', '***'],]

    for i in range(3):
        print()
    style1 = CellStyle(heading_style=TextStyle.Reverse.value, plain_style='')
    style2 = CellStyle(
        heading_style=TextStyle.Bold.value + BgColor.Red.value + FgColor.White.value,
        plain_style=TextStyle.Italic.value + BgColor.BrightBlue.value)
    t = Table(default_style=style1)
    t.populate(content=cell_contents,
               column_formats=cell_formats,
               column_alignment=cell_alignment)
    # Override header formatting.
    for col_idx in range(t.width):
        c = t.cell_at(column=col_idx, row=0)
        c.fmt = 's'
        c.alignment = Alignment.Center
        c.is_heading = True
    lines = t.render(OutputFormat.TEXT, LineStyle.light)
    print_lines(lines)
    lines = t.render(OutputFormat.ANSI, LineStyle.double)
    print_lines(lines)
    # Override styling of diagonal cells.
    for i in range(min(t.height, t.width)):
        t.cell_at(i, i).style = style2
    lines = t.render(OutputFormat.ANSI, LineStyle.heavy)
    print_lines(lines)


def demo_table_advanced():
    """Demonstrate advanced use of the Table class."""
    print('Demonstrate advanced use of the Table class.')
    ds = CellStyle(TextStyle.Bold.value + TextStyle.Italic.value, '')
    cells = [ [
        TableCell('First', is_heading=True, alignment=Alignment.Left, style=ds),
        TableCell('Second', is_heading=True, alignment=Alignment.Center,
                  style=ds, join_right=True),
        TableCell('Third', is_heading=True, alignment=Alignment.Left, style=ds),
        TableCell('Fourth', is_heading=True, alignment=Alignment.Right, style=ds),
        TableCell('Fifth', is_heading=True, alignment=Alignment.Left, style=ds),
    ] ]  # cells
    cells.append([
        TableCell(1, '3d', alignment=Alignment.Right, style=ds),
        TableCell('This is a text that will not fit in the table.'
                  ' This is because it is too long for a single cell.',
                  alignment=Alignment.Center, style=ds, join_right=True),
        TableCell('3', join_right=True),
        TableCell(4, '5d'),
        TableCell('***', alignment=Alignment.Left, style=ds),
    ])
    cells.append([
        TableCell(2, '3d', alignment=Alignment.Right, style=ds),
        TableCell('This will fit easily.',
                  alignment=Alignment.Center, style=ds),
        TableCell('First time'),
        TableCell(44, '5d'),
        TableCell('***', alignment=Alignment.Center, style=ds),
    ])
    cells.append([
        TableCell(3, '3d', alignment=Alignment.Right, style=ds, join_right=True),
        TableCell('Not seen', style=ds),
        TableCell('2nd time', alignment=Alignment.Left, style=ds),
        TableCell(444, '5d', style=ds),
        TableCell('***', alignment=Alignment.Right, style=ds),
    ])
    cells.append([
        TableCell(4, '3d', alignment=Alignment.Right, style=ds, join_right=True),
        TableCell('not seen', style=ds, join_right=True),
        TableCell('not seen', style=ds),
        TableCell(4444, '5d', style=ds),
        TableCell('*', alignment=Alignment.Left, style=ds),
    ])
    cells.append([
        TableCell(5, '3d', alignment=Alignment.Right, style=ds, join_right=True),
        TableCell('not seen', style=ds, join_right=True),
        TableCell('not seen', style=ds, join_right=True),
        TableCell(44444, '5d', style=ds),
        TableCell(' *', alignment=Alignment.Left, style=ds),
    ])
    cells.append([
        TableCell(6, '3d', alignment=Alignment.Right, style=ds, join_right=True),
        TableCell('not seen', style=ds, join_right=True),
        TableCell('not seen', style=ds, join_right=True),
        TableCell(444444, '5d', style=ds, join_right=True),
        TableCell('  *', alignment=Alignment.Left, style=ds),
    ])
    t = Table(cells, default_style=ds)
    t.set_column_width(1, 10)
    lines = t.render(OutputFormat.ANSI, LineStyle.light)
    print_lines(lines)
    lines = t.render(OutputFormat.TEXT, LineStyle.heavy)
    print_lines(lines)


def demo():
    """Littlejonny demo."""
    print_lines(draw_box(5, 3, LineStyle.light))
    print_lines(draw_box(1, 1, LineStyle.double))
    print_lines(draw_box(40, 3, LineStyle.heavy))

    b1 = Box(8, 3, 17, 9, LineStyle.light,
             FgColor.Green.value + BgColor.White.value,
             FgColor.Blue.value + BgColor.BrightYellow.value + TextStyle.Italic.value)
    b1.text = [
        '(8;7)      (17;8)',
        '',
        '',
        '',
        '        *       ',
        '',
        '',
        '',
        '(8;16)    (17;16)',
    ]
    b2 = Box(1, 1, 64, 13, LineStyle.double,
             FgColor.Black.value + BgColor.Green.value,
             FgColor.Red.value + BgColor.BrightWhite.value + TextStyle.Bold.value)
    b2.text = [
        '         1         2         3         4         5         6    ',
        '1234567890123456789012345678901234567890123456789012345678901234',
        '',
        '                                                           right',
        'left',
        '                               center',
        UC.box_drawings.light.horizontal * b2.width,
        'ABC DEF GHI JKL MNO PRQ STU VWX YZ!',
        'ABC DEF GHI JKL MNO PRQ STU VWX YZ!',
        UC.box_drawings.light.horizontal * b2.width,
    ]
    print_lines(b1.render(OutputFormat.TEXT))
    print_lines(b2.render(OutputFormat.TEXT))

    b3 = Box(4, 4, 20, 9)
    b3.flow_text('This is a really long text to flow into the box that is'
                 ' just a tiny little thing of a box. '
                 'OMG_this_will_never_fit_into_a_single_line'
                 ' :)')
    print_lines(b3.render(OutputFormat.TEXT))

    # row[column]
    ct1 = ColumnTable()
    ct1.set_table_transposed(
        headings=['First', 'Second', 'Third', 'Fourth'],
        cell_formats=['3d', '08x', 's', '>s'],
        cells=[[1, 0x12345678, 'abc def geh', 'this is a sample text'],
               [2, 0xffffee01, '12345', 'Short'],
               [12, -1, 'minus one', 'negative hex number'],
               [123, 0, 'zero', 'Zero hexadecimal number'],
               [1000, 23, 'First', 'The first column is too large.']]
    )
    print_lines(ct1.draw(LineStyle.light))

    # column[row]
    ct2 = ColumnTable()
    ct2.set_table(
        headings=['First', 'Second', 'Third', 'Fourth'],
        cell_formats=['3d', '08x', 's', '>s'],
        cells=[[1, 2, 12, 123, 1000],
               [0x12345678, 0xffffee01, -1, 0, 23],
               ['abc def geh', '12345', 'minus one', 'zero', 'First'],
               ['this is a sample text', 'Short', 'negative hex number',
                'Zero hexadecimal number', 'The first column is too large.']]
    )
    print_lines(ct2.draw(LineStyle.light))
    print_lines(b1.render(OutputFormat.ANSI))
    print_lines(b2.render(OutputFormat.ANSI))

    demo_table_simple()
    demo_table_advanced()


if __name__ == '__main__':
    demo()
