#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2023 by Christian Dönges
# SPDXID: SPDXRef-ansi-terminal-py
"""Handle console operations on an ANSI-compliant terminal.

.. see: https://en.wikipedia.org/wiki/ANSI_escape_code

.. deprecated:: 1.6.0 Will be removed in 2.0.

"""
import enum
import logging
import os
import re
import sys
from dataclasses import dataclass
from math import log2
from time import sleep


if os.name != 'nt':
    # termios is a POSIX API not available on Windows.
    import termios
    import tty
else:
    from ctypes import byref, c_int, windll
    import msvcrt


@enum.unique
class BgColor(enum.Enum):
    """Background colors and the ANSI format strings used to create them."""
    Black = '\x1B[40m'
    Red = '\x1B[41m'
    Green = '\x1B[42m'
    Yellow = '\x1B[43m'
    Blue = '\x1B[44m'
    Magenta = '\x1B[45m'
    Cyan = '\x1B[46m'
    White = '\x1B[47m'
    BrightBlack = '\x1B[100m'
    BrightRed = '\x1B[101m'
    BrightGreen = '\x1B[102m'
    BrightYellow = '\x1B[103m'
    BrightBlue = '\x1B[104m'
    BrightMagenta = '\x1B[105m'
    BrightCyan = '\x1B[106m'
    BrightWhite = '\x1B[107m'


@enum.unique
class FgColor(enum.Enum):
    """Foreground colors and the ANSI format strings used to create them."""
    Black = '\x1B[30m'
    Red = '\x1B[31m'
    Green = '\x1B[32m'
    Yellow = '\x1B[33m'
    Blue = '\x1B[34m'
    Magenta = '\x1B[35m'
    Cyan = '\x1B[36m'
    White = '\x1B[37m'
    BrightBlack = '\x1B[90m'
    BrightRed = '\x1B[91m'
    BrightGreen = '\x1B[92m'
    BrightYellow = '\x1B[93m'
    BrightBlue = '\x1B[94m'
    BrightMagenta = '\x1B[95m'
    BrightCyan = '\x1B[96m'
    BrightWhite = '\x1B[97m'


@dataclass
class AnsiColor:
    """24 bit RGB color for use with ANSI terminals.

    There are three components, each of which must be 0..255:

        - red
        - green
        - blue

    Note that not all terminals support 24 bit colors.
    """
    red: int = 0
    green: int = 0
    blue: int = 0

    @property
    def bg(self) -> str:
        """Return a string to set the background to this color."""
        return f'\x1B[48;2;{self.red};{self.green};{self.blue}m'

    @property
    def fg(self) -> str:
        """Return a string to set the foreground to this color."""
        return f'\x1B[38;2;{self.red};{self.green};{self.blue}m'


class AnsiControl:
    """Popular ANSI control sequences."""

    @staticmethod
    def erase_line():
        """Erase the current line."""
        return '\x1B[2K'

    @staticmethod
    def erase_screen():
        """Erase the entire screen content.

        Depending on the terminal, this may scroll up the entire screen, so the
        screen content will be saved to the scrollback buffer.
        """
        return '\x1B[2J'

    @staticmethod
    def erase_scrollback_buffer():
        """Erase the scrollback buffer without erasing the screen content."""
        return '\x1B[3J'

    @staticmethod
    def erase_to_end_of_line():
        """Erase from the cursor position to the end of the current line."""
        return '\x1B[0K'

    @staticmethod
    def erase_to_start_of_line():
        """Erase from the cursor position to the start of the current line."""
        return '\x1B[1K'

    @staticmethod
    def move_cursor_to(column: int = 1, row: int = 1) -> str:
        """Move the cursor to the given position.

        :param int column: New cursor column (x-position).
        :param int row: New cursor row (y-position).
        :return: Control sequence.
        :rtype str:
        :raise ValueError: The row or column is less than 1.
        """
        if row < 1:
            raise ValueError('row too small')
        if column < 1:
            raise ValueError('column too small')
        return f'\x1b[{row};{column}H'

    @staticmethod
    def move_cursor_back(nr_columns: int = 1) -> str:
        """Move the cursor back by `nr_columns` columns.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_columns: Number of columns to move the cursor by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: The number of columns is less than 1.
        """
        if nr_columns < 1:
            raise ValueError('too few columns')
        return f'\x1b[{nr_columns}D'

    @staticmethod
    def move_cursor_down(nr_rows: int = 1):
        """Move the cursor down by `nr_rows` rows.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_rows: Number of rows to move the cursor by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: The number of rows is less than 1.
        """
        if nr_rows < 1:
            raise ValueError('too few rows')
        return f'\x1b[{nr_rows}B'

    @staticmethod
    def move_cursor_forward(nr_columns: int = 1):
        """Move the cursor forward by `nr_columns` columns.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_columns: Number of columns to move the cursor by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: The number of columns is less than 1.
        """
        if nr_columns < 1:
            raise ValueError('too few columns')
        return f'\x1b[{nr_columns}C'

    @staticmethod
    def move_cursor_up(nr_rows: int = 1):
        """Move the cursor up by `nr_rows` rows.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_rows: Number of rows to move the cursor by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: The number of rows is less than 1.
        """
        if nr_rows < 1:
            raise ValueError('too few rows')
        return f'\x1b[{nr_rows}A'

    @staticmethod
    def scroll_page_down(nr_pages: int = 1):
        """Scroll down by nr_pages pages/screens.

        :param int nr_pages: Number of pages to scroll down by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: nr_pages is < 1
        """
        if nr_pages < 1:
            raise ValueError('scroll down at least one page')
        return f'\x1B{nr_pages}T'

    @staticmethod
    def scroll_page_up(nr_pages: int = 1):
        """Scroll up by nr_pages pages/screens.

        :param int nr_pages: Number of pages to scroll up by.
        :return: Control sequence.
        :rtype str:
        :raise ValueError: nr_pages is < 1
        """
        if nr_pages < 1:
            raise ValueError('scroll up at least one page')
        return f'\x1B{nr_pages}S'


@enum.unique
class TextStyle(enum.Enum):
    """Text styles and the ANSI format strings used to create them."""
    Reset = '\x1B[0m'  # All attributes off.
    Bold = '\x1B[1m'
    Faint = '\x1B[2m'
    Italic = '\x1B[3m'
    Underline = '\x1B[4m'
    SlowBlink = '\x1B[5m'  # Text blinks less than 150 times per minute.
    RapidBlink = '\x1B[6m'  # Text blinks more than 150 times per minute. Not widely supported.
    Reverse = '\x1B[7m'  # Swaps foreground and background colors. Inconsistently implemented.
    Hide = '\x1B[8m'  # Not widely supported.
    StrikeOut = '\x1B[9m'  # Characters marked for deltetion. Not supported in Terminal.app.
    PrimaryFont = '\x1B[10m'
    AlternateFont1 = '\x1B[11m'
    AlternateFont2 = '\x1B[12m'
    AlternateFont3 = '\x1B[13m'
    AlternateFont4 = '\x1B[14m'
    AlternateFont5 = '\x1B[15m'
    AlternateFont6 = '\x1B[16m'
    AlternateFont7 = '\x1B[17m'
    AlternateFont8 = '\x1B[18m'
    AlternateFont9 = '\x1B[19m'
    GothicFont = '\x1B[20m'  # Rarely supprorted.
    DoubleUnderline = '\x1B[21m'  # Often NoBold.
    NormalIntensity = '\x1B[22m'  # Neither Bold nor Faint.
    NoItalic = '\x1B[23m'
    NoUnderline = '\x1B[24m'
    NoBlink = '\x1B[25m'
    NoReverse = '\x1B[27m'
    NoHide = '\x1B[28m'
    NoStrikeOut = '\x1B[29m'
    Frame = '\x1B[51m'
    Encircle = '\x1B[52m'
    Overline = '\x1B[53m'
    Superscript = '\x1B[73m'
    Subscript = '\x1B[74m'
    NoSuperSub = '\x1B[75m'  # Neither Superscript nor Subscript.


@dataclass
class ColsRows:
    """A column and row position or size."""
    column: int
    row: int

    def __str__(self) -> str:
        """Return a string representation of the instance."""
        return f'({self.column};{self.row})'


def enable_vt100_mode_on_windows():
    """If on Windows, enable VT100 mode to allow processing of ANSI codes.

        :doc: https://bugs.python.org/issue29059
    """
    if os.name != 'nt':
        return
    stdout_handle = windll.kernel32.GetStdHandle(c_int(-11))  # stdout is 11 on windows
    old_mode = c_int(0)
    windll.kernel32.GetConsoleMode(c_int(stdout_handle), byref(old_mode))
    new_mode = c_int(old_mode.value | 4)  # ENABLE_VIRTUAL_TERMINAL_PROCESSING
    windll.kernel32.SetConsoleMode(c_int(stdout_handle), new_mode)


@dataclass
class AnsiTerminal:
    full: bool = False  # True: full cursor control
    autoflush: bool = False  # automatically flush
    _cursor_column: int = -1
    _cursor_row: int = -1
    _fin = sys.stdin.fileno()
    _fout = sys.stdout.fileno()
    _have_posix: bool = (os.name != 'nt')  # Running on a POSIX system (True) or Windows (False)?
    _logger: logging.Logger = logging.getLogger(__name__)
    _terminal_columns: int = -1
    _terminal_rows: int = -1

    def __post_init__(self):
        if not sys.stdin.isatty():
            self._logger.error('stdin is not a TTY.')
            raise EnvironmentError('stdin not a TTY')
        if not sys.stdout.isatty():
            self._logger.error('stdout is not a TTY.')
            raise EnvironmentError('stdout not a TTY')
        enable_vt100_mode_on_windows()
        if self.full and not sys.stdin.readable():
            self._logger.warning('stdin is not readable, running without full mode.')
            self.full = False
        self._determine_current_cursor()
        (self._terminal_columns, self._terminal_rows) = os.get_terminal_size(self._fout)

    def _determine_current_cursor(self):
        """Determine the current cursor position."""
        self._logger.debug('%s._determine_current_cursor()', self.__class__.__name__)
        if not self.full:
            self._logger.debug('Current cursor [fake]: (1;1)')
            self._cursor_column = 1
            self._cursor_row = 1
            return

        if self._have_posix:
            reply = self._get_current_cursor_posix()
        else:
            reply = self._get_current_cursor_windows()

        m = re.match(r'\x1b\[(?P<row>\d+);(?P<col>\d+)R', reply)
        if m is None:
            self._logger.error('Expected DSR response "ESC[row;colR" got "%s".',
                               reply.encode('utf-8').hex())
            raise ValueError('unexpected DSR response')
        self._cursor_row = int(m.group('row'))
        self._cursor_column = int(m.group('col'))
        self._logger.debug('Current cursor: (%d;%d)', self._cursor_column, self._cursor_row)

    def _get_current_cursor_posix(self) -> str:
        """Return a string containing the current cursor position on POSIX."""
        tattr = termios.tcgetattr(self._fin)
        reply = ''
        try:
            # Switch to CBreak mode.
            tty.setcbreak(self._fin, termios.TCSANOW)
            sys.stdout.write('\x1b[6n')  # DSR - Display Status Request
            sys.stdout.flush()

            while True:
                reply += sys.stdin.read(1)
                if reply[-1] == 'R':
                    break
        except RuntimeError as e:
            self._logger.error('While reading: %s', e)
        finally:
            # Restore previous mode.
            termios.tcsetattr(self._fin, termios.TCSANOW, tattr)

        return reply

    def _get_current_cursor_windows(self) -> str:
        """Return a string containing the current cursor position on Windows.

            :doc: https://stackoverflow.com/a/69006335
        """
        reply = ''
        try:
            sys.stdout.write('\x1b[6n')  # DSR - Display Status Request
            sys.stdout.flush()

            input_pending = True
            while input_pending:
                # Read a single keypress from the keyboard input buffer.
                reply += msvcrt.getch().decode('ascii')
                # Is there more in the input buffer?
                input_pending = msvcrt.kbhit()
        except RuntimeError as e:
            self._logger.error('While reading: %s', e)

        return reply

    def _update_cursor_position(self, column_delta: int, row_delta: int):
        """Update the cached cursor position with the given delta.

           The cursor position is bounded by the screen, so it is always
           valid.

           :param int column_delta: Number of columns the cursor was moved
               left (negative) or right (positive).
           :param int row_delta: Number of rows the cursor was moded
                up (negative) or down (positive).
        """
        self._logger.debug('_update_cursor_position(%d, %d)', column_delta, row_delta)
        self._cursor_column += column_delta
        if self._cursor_column < 1:
            self._cursor_column = 1
        elif self._cursor_column > self._terminal_columns:
            self._cursor_column = self._terminal_columns

        self._cursor_row += row_delta
        if self._cursor_row < 1:
            self._cursor_row = 1
        elif self._cursor_row > self._terminal_rows:
            self._cursor_row = self._terminal_rows

    def cursor_position(self, use_cached: bool = False) -> ColsRows:
        """Return the current cursor position.

        :param bool use_cached: If `True`, the positioned cached by the instance
            is used. This is faster than `False`, which queries the terminal,
            but could be wrong.
        :return: Current position of the cursor.
        :rtype: ColsRows
        """
        if not use_cached:
            self._determine_current_cursor()
        return ColsRows(column=self._cursor_column, row=self._cursor_row)

    def erase_line(self):
        """Erase the current line."""
        self._logger.debug('erase_line()')
        sys.stdout.write(AnsiControl.erase_line())
        if self.autoflush:
            sys.stdout.flush()

    def erase_screen(self):
        """Erase the entire screen content.

        Depending on the terminal, this may scroll up the entire screen, so the
        screen content will be saved to the scrollback buffer.
        """
        self._logger.debug('erase_screen()')
        sys.stdout.write(AnsiControl.erase_screen())
        if self.autoflush:
            sys.stdout.flush()

    def erase_scrollback_buffer(self):
        """Erase the scrollback buffer without erasing the screen content."""
        self._logger.debug('erase_scrollback_buffer()')
        sys.stdout.write(AnsiControl.erase_scrollback_buffer())
        if self.autoflush:
            sys.stdout.flush()


    def erase_to_end_of_line(self):
        """Erase from the cursor position to the end of the current line."""
        self._logger.debug('erase_to_end_of_line()')
        sys.stdout.write(AnsiControl.erase_to_end_of_line())
        if self.autoflush:
            sys.stdout.flush()

    def erase_to_start_of_line(self):
        """Erase from the cursor position to the start of the current line."""
        self._logger.debug('erase_to_start_of_line()')
        sys.stdout.write(AnsiControl.erase_to_start_of_line())
        if self.autoflush:
            sys.stdout.flush()

    def move_cursor_to(self, column: int = 1, row: int = 1):
        """Move the cursor to the given position.

        :param int column: New cursor column (x-position).
        :param int row: New cursor row (y-position).
        """
        self._logger.debug('move_cursor_to(%d, %d)', column, row)
        if column > self._terminal_columns or column <= 0:
            raise ValueError('column out of range')
        if row > self._terminal_rows or row <= 0:
            raise ValueError('row out of range')
        sys.stdout.write(AnsiControl.move_cursor_to(column=column, row=row))
        self._cursor_column = column
        self._cursor_row = row
        if self.autoflush:
            sys.stdout.flush()

    def move_cursor_back(self, nr_columns: int = 1):
        """Move the cursor back by `nr_columns` columns.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_columns: Number of columns to move the cursor by.
        """
        self._logger.debug('move_cursor_back(%d)', nr_columns)
        if nr_columns < 1:
            raise ValueError('too few rows')
        sys.stdout.write(AnsiControl.move_cursor_back(nr_columns))
        self._update_cursor_position(-nr_columns, 0)
        if self.autoflush:
            sys.stdout.flush()

    def move_cursor_down(self, nr_rows: int = 1):
        """Move the cursor down by `nr_rows` rows.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_rows: Number of rows to move the cursor by.
        """
        self._logger.debug('move_cursor_down(%d)', nr_rows)
        if nr_rows < 1:
            raise ValueError('too few rows')
        sys.stdout.write(AnsiControl.move_cursor_down(nr_rows))
        self._update_cursor_position(0, nr_rows)
        if self.autoflush:
            sys.stdout.flush()

    def move_cursor_forward(self, nr_columns: int = 1):
        """Move the cursor forward by `nr_columns` columns.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_columns: Number of columns to move the cursor by.
        """
        self._logger.debug('move_cursor_forward(%d)', nr_columns)
        if nr_columns < 1:
            raise ValueError('too few rows')
        sys.stdout.write(AnsiControl.move_cursor_forward(nr_columns))
        self._update_cursor_position(nr_columns, 0)
        if self.autoflush:
            sys.stdout.flush()

    def move_cursor_up(self, nr_rows: int = 1):
        """Move the cursor up by `nr_rows` rows.

        If the cursor is at the edge of the screen, this has no effect.

        :param int nr_rows: Number of rows to move the cursor by.
        """
        self._logger.debug('move_cursor_up(%d)', nr_rows)
        if nr_rows < 1:
            raise ValueError('too few rows')
        sys.stdout.write(AnsiControl.move_cursor_up(nr_rows))
        self._update_cursor_position(0, -nr_rows)
        if self.autoflush:
            sys.stdout.flush()

    def scroll_page_down(self, nr_pages: int = 1):
        """Scroll down by nr_pages pages/screens.

        :param int nr_pages: Number of pages to scroll down by.
        :raise ValueError: nr_pages is < 1
        """
        self._logger.debug('scroll_page_down(%d)', nr_pages)
        if nr_pages < 1:
            raise ValueError('scroll down at least one page')
        sys.stdout.write(AnsiControl.scroll_page_down(nr_pages))
        if self.autoflush:
            sys.stdout.flush()

    def scroll_page_up(self, nr_pages: int = 1):
        """Scroll up by nr_pages pages/screens.

        :param int nr_pages: Number of pages to scroll up by.
        :raise ValueError: nr_pages is < 1
        """
        self._logger.debug('scroll_page_up(%d)', nr_pages)
        if nr_pages < 1:
            raise ValueError('scroll up at least one page')
        sys.stdout.write(AnsiControl.scroll_page_up(nr_pages))
        if self.autoflush:
            sys.stdout.flush()

    @property
    def terminal_size(self) -> ColsRows:
        """Number of columns and rows in the terminal.

        :return: Number of columns and rows of the terminal.
        :rtype ColsRows:
        """
        return ColsRows(self._terminal_columns, self._terminal_rows)


def showcase_3bit_colors():
    """Print a color chart."""
    print(f'''{TextStyle.Reset.value}Classic Color Chart
                   Normal                  Bright
    Black   {FgColor.Black.value}Foreground{TextStyle.Reset.value} {BgColor.Black.value}Background{TextStyle.Reset.value}   {FgColor.BrightBlack.value}Foreground{TextStyle.Reset.value} {BgColor.BrightBlack.value}Background{TextStyle.Reset.value}
    Red     {FgColor.Red.value}Foreground{TextStyle.Reset.value} {BgColor.Red.value}Background{TextStyle.Reset.value}   {FgColor.BrightRed.value}Foreground{TextStyle.Reset.value} {BgColor.BrightRed.value}Background{TextStyle.Reset.value}
    Green   {FgColor.Green.value}Foreground{TextStyle.Reset.value} {BgColor.Green.value}Background{TextStyle.Reset.value}   {FgColor.BrightGreen.value}Foreground{TextStyle.Reset.value} {BgColor.BrightGreen.value}Background{TextStyle.Reset.value}
    Yellow  {FgColor.Yellow.value}Foreground{TextStyle.Reset.value} {BgColor.Yellow.value}Background{TextStyle.Reset.value}   {FgColor.BrightYellow.value}Foreground{TextStyle.Reset.value} {BgColor.BrightYellow.value}Background{TextStyle.Reset.value}
    Blue    {FgColor.Blue.value}Foreground{TextStyle.Reset.value} {BgColor.Blue.value}Background{TextStyle.Reset.value}   {FgColor.BrightBlue.value}Foreground{TextStyle.Reset.value} {BgColor.BrightBlue.value}Background{TextStyle.Reset.value}
    Magenta {FgColor.Magenta.value}Foreground{TextStyle.Reset.value} {BgColor.Magenta.value}Background{TextStyle.Reset.value}   {FgColor.BrightMagenta.value}Foreground{TextStyle.Reset.value} {BgColor.BrightMagenta.value}Background{TextStyle.Reset.value}
    Cyan    {FgColor.Cyan.value}Foreground{TextStyle.Reset.value} {BgColor.Cyan.value}Background{TextStyle.Reset.value}   {FgColor.BrightCyan.value}Foreground{TextStyle.Reset.value} {BgColor.BrightCyan.value}Background{TextStyle.Reset.value}
    White   {FgColor.White.value}Foreground{TextStyle.Reset.value} {BgColor.White.value}Background{TextStyle.Reset.value}   {FgColor.BrightWhite.value}Foreground{TextStyle.Reset.value} {BgColor.BrightWhite.value}Background{TextStyle.Reset.value}

    ''')


def showcase_24_bit_colors():
    """Print color chart."""
    from math import sqrt

    print(f"""{TextStyle.Reset.value}24 bit Color Chart
    """)
    size = 16
    nr_rows = int(sqrt(size ** 3))
    nr_cols = nr_rows
    color_bits = int(log2(size))
    color_mask = (0xFF << color_bits) & 0xFF
    # Note [[''*nr_cols]**nr_rows] does not work because all
    # rows will contain references to the same columns.
    matrix = [['' for col in range(nr_cols)] for r in range(nr_rows)]
    for i in range(size ** 3):
        x = i & (nr_cols - 1)
        y = int(i / nr_rows)
        r = (i << color_bits) & color_mask
        g = i & color_mask
        b = (i >> color_bits) & color_mask
        color = AnsiColor(r, g, b)
        matrix[y][x] = f'{color.bg} '
    for row in matrix:
        sys.stdout.write(''.join(row))
        sys.stdout.write(f'{TextStyle.Reset.value}\n')
    sys.stdout.flush()


def showcase_text_styles():
    """Show all implemented text styles."""
    sys.stdout.write(f'''\nText Styles

    Reset            {TextStyle.Reset.value}Reset{TextStyle.Reset.value}
    Bold             {TextStyle.Bold.value}Bold{TextStyle.NormalIntensity.value}             NormalIntensity{TextStyle.Reset.value}
    Faint            {TextStyle.Faint.value}Faint{TextStyle.NormalIntensity.value}            NormalIntensity{TextStyle.Reset.value}
    Italic           {TextStyle.Italic.value}Italic{TextStyle.NoItalic.value}           NoItalic{TextStyle.Reset.value}
    Underline        {TextStyle.Underline.value}Underline{TextStyle.NoUnderline.value}        NoUnderline{TextStyle.Reset.value}
    SlowBlink        {TextStyle.SlowBlink.value}SlowBlink{TextStyle.NoBlink.value}        NoBlink{TextStyle.Reset.value}
    RapidBlink       {TextStyle.RapidBlink.value}RapidBlink{TextStyle.NoBlink.value}       NoBlink{TextStyle.Reset.value}
    Reverse          {TextStyle.Reverse.value}Reverse{TextStyle.NoReverse.value}          NoReverse{TextStyle.Reset.value}
    Hide             {TextStyle.Hide.value}Hide{TextStyle.NoHide.value}             NoHide{TextStyle.Reset.value}
    StrikeOut        {TextStyle.StrikeOut.value}StrikeOut{TextStyle.NoStrikeOut.value}        NoStrikeOut{TextStyle.Reset.value}
    PrimaryFont      {TextStyle.PrimaryFont.value}PrimaryFont{TextStyle.Reset.value}
    AlternateFont1   {TextStyle.AlternateFont1.value}AlternateFont1{TextStyle.Reset.value}
    AlternateFont2   {TextStyle.AlternateFont2.value}AlternateFont2{TextStyle.Reset.value}
    AlternateFont3   {TextStyle.AlternateFont3.value}AlternateFont3{TextStyle.Reset.value}
    AlternateFont4   {TextStyle.AlternateFont4.value}AlternateFont4{TextStyle.Reset.value}
    AlternateFont5   {TextStyle.AlternateFont5.value}AlternateFont5{TextStyle.Reset.value}
    AlternateFont6   {TextStyle.AlternateFont6.value}AlternateFont6{TextStyle.Reset.value}
    AlternateFont7   {TextStyle.AlternateFont7.value}AlternateFont7{TextStyle.Reset.value}
    AlternateFont8   {TextStyle.AlternateFont8.value}AlternateFont8{TextStyle.Reset.value}
    AlternateFont9   {TextStyle.AlternateFont9.value}AlternateFont9{TextStyle.Reset.value}
    GothicFont       {TextStyle.GothicFont.value}GothicFont{TextStyle.Reset.value}
    DoubleUnderline  {TextStyle.DoubleUnderline.value}DoubleUnderline{TextStyle.Reset.value}
    Frame            {TextStyle.Frame.value}Frame{TextStyle.Reset.value}
    Encircle         {TextStyle.Encircle.value}Encircle{TextStyle.Reset.value}
    Overline         {TextStyle.Overline.value}Overline{TextStyle.Reset.value}
    Superscript      {TextStyle.Superscript.value}Superscript{TextStyle.NoSuperSub.value}      NoSuperSub{TextStyle.Reset.value}
    Subscript        {TextStyle.Subscript.value}Subscript{TextStyle.NoSuperSub.value}        NoSuperSub{TextStyle.Reset.value}
    ''')


def showcase_cursor(at: AnsiTerminal):
    """Show cursor movements."""
    from pymisclib.unicodechars import UC

    delay = 0.2
    ts = at.terminal_size

    def show_cursor_position():
        """Print the cursor position in the bottom-left corner."""
        cp = at.cursor_position()
        at.move_cursor_to(ts.column - 7, ts.row)
        sys.stdout.write(f'{cp.column:3d},{cp.row:3d}')
        at.move_cursor_to(cp.column, cp.row)

    sys.stdout.write('\n')
    for l in range(ts.row):
        sys.stdout.write(chr(l + 64) * ts.column)
        sys.stdout.write('\n')
    at.erase_screen()
    at.erase_scrollback_buffer()
    show_cursor_position()
    sleep(delay * 5)

    at.move_cursor_to(1, 1)
    cp1 = at.cursor_position()
    if cp1.column != 1 or cp1.row != 1:
        print('Cursor positions are broken.')
        return
    show_cursor_position()
    sys.stdout.write('\nCursor\n')
    sleep(delay)

    sys.stdout.write('Full line             : 12345678901234567890\n')
    sys.stdout.write('Erase to end of line  : 12345678901234567890')
    at.move_cursor_back(10)
    show_cursor_position()
    sleep(delay * 5)
    at.erase_to_end_of_line()
    sleep(delay)
    sys.stdout.write('\n')
    sys.stdout.write('Erase to start of line: 12345678901234567890')
    at.move_cursor_back(10)
    show_cursor_position()
    sleep(delay * 5)
    at.erase_to_start_of_line()
    sleep(delay)
    sys.stdout.write('\n')
    sys.stdout.write('Erase to entire line  : 12345678901234567890')
    at.move_cursor_back(10)
    show_cursor_position()
    sleep(delay * 5)
    at.erase_line()
    sleep(delay)

    at.move_cursor_down(10)
    show_cursor_position()
    sleep(delay)
    for c in range(40):
        sys.stdout.write(UC.arrows.rightwards_arrow)
        at.move_cursor_back(1)
        at.move_cursor_forward(1)
        show_cursor_position()
        sleep(delay)
    for r in range(5):
        sys.stdout.write(UC.arrows.upwards_arrow)
        at.move_cursor_back(1)
        at.move_cursor_up(1)
        show_cursor_position()
        sleep(delay)
    for c in range(20):
        sys.stdout.write(UC.arrows.leftwards_arrow)
        at.move_cursor_back(1)
        at.move_cursor_back(1)
        show_cursor_position()
        sleep(delay)
    for r in range(5):
        sys.stdout.write(UC.arrows.downwards_arrow)
        at.move_cursor_back(1)
        at.move_cursor_down(1)
        show_cursor_position()
        sleep(delay)
    at.move_cursor_to(1, ts.row)
    print('Done')


def main():
    """Test routine."""
    import os
    os.system('')  # enables ansi escape characters in terminal

    at = AnsiTerminal(full=True, autoflush=True)
    at.erase_screen()

    showcase_cursor(at)
    showcase_3bit_colors()
    showcase_24_bit_colors()
    showcase_text_styles()


if __name__ == '__main__':
    main()
