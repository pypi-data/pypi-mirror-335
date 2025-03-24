#!/usr/bin/env python3
# vim ts=4,fileencoding=utf-8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2012-2022, 2023, 2024, 2025 by Christian Dönges
# SPDXID: SPDXRef-utilities-py
"""Collection of various utility functions.
"""

# pylint: disable=invalid-name

import argparse
import bz2
import codecs
import contextlib
import ctypes
import glob
import gzip
import locale
import logging
import lzma
import math
import os
import re
import shutil
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path
from pprint import pformat
from time import mktime
from typing import Any, Generator
from zipfile import ZipFile, ZipInfo


from pymisclib.xmlutils import log_xml


# Globals (use sparingly)
logger = logging.getLogger(__name__)


def dir_path(path: str) -> Path:
    """Convert the string to a path and return it if it is a directory.

        This function is intended to be used as the `type` argument to :func:`Argparser.add_argument`.

        :param str path: String containing path to check.
        :return: Path to a directory.
        :rtype: Path

        :raise argparse.ArgumentTypeError: The string was not a valid path to a directory.
    """
    if not os.path.isdir(path):
        raise argparse.ArgumentTypeError(
            f'"{path}" is not a valid path to a directory')
    return Path(path)


def exit_hard(returncode: int = 0):
    """Terminate the running application.

        :param int returncode: Exit code to return to spawning shell.
    """
    os._exit(returncode)  # pylint: disable=protected-access


def extract_from_zip_preserving_mtime(zip_file: ZipFile,
                                      zip_info: ZipInfo,
                                      out_path: dir_path):
    """Extract file from a ZIP archive preserving the modification time.

        :param ZipFile zip_file: The archive to extract from.
        :param ZipInfo zip_info: The information about the file to extract.
        :param dir_path out_path: Destination directory for the extracted
            file (must exist).

        :see: https://stackoverflow.com/q/9813243
    """
    zip_file.extract(zip_info, out_path)
    # Add (0, 0, -1) to the time to indicate we do not know if DST was active.
    date_time = mktime(zip_info.date_time + (0, 0, -1))
    # Set ctime and mtime of the extracted file.
    os.utime(out_path / zip_info.filename, (date_time, date_time))


def file_path(path: str) -> Path:
    """Convert the string to a path and return it if it is a file.

        :param str path: String containing path to check.
        :return: Path to a file.
        :rtype: Path

        :raise argparse.ArgumentTypeError: The string did not contain a valid
            path to a file.
    """
    if not os.path.isfile(path):
        raise argparse.ArgumentTypeError(
            f'"{path}" is not a valid path to a file')
    return Path(path)



def get_language() -> str:
    """Determine the language the current user has set their OS to."""
    if os.name == 'posix':
        # BSD, Darwin, and Linux make it easy.
        lang = os.environ['LANG'].split('.')[0]
    elif os.name == 'nt':
        windll = ctypes.windll.kernel32
        lang = locale.windows_locale[windll.GetUserDefaultUILanguage()]
    else:
        raise RuntimeError(f'unknown OS: {os.name}')
    return lang


def hexdump(b: bytes,
            bytes_per_line: int = 16,
            start_offset: int = 0,
            offset_digits: int = 8,
            show_ascii: bool = True) -> Generator[str, None, None]:
    """Generator function to create a pretty representation of the given bytes and return a line per call.

        ```
        first_prefix   00000000  64 65 66 67 68 69 6A 6B  @ABCDEFG
        always_prefix  00000000  64 65 66 67 68 69 6A 6B  @ABCDEFG
        ```

        :param bytes b: The bytes to print.
        :param int bytes_per_line: Number of bytes per line.
        :param int start_offset:   Starting offset for the first byte.
        :param int offset_digits:  Number of digits in the offset.
        :param bool show_ascii: Print ASCII characters after the hex dump if True.
        :return: A single hexdump line per call. None when done.
        :rtype: Generator[str, None, None]
    """
    length = len(b)
    offset = 0
    if length <= bytes_per_line:
        show_offset = False
    else:
        show_offset = True
    while length > 0:
        if length < bytes_per_line:
            bytes_per_line = length
        b_slice = b[offset:offset + bytes_per_line]
        hs = b_slice.hex(' ')
        if show_offset:
            s = f'{offset + start_offset:0{offset_digits}x}  {hs}  '
        else:
            s = f'{hs}  '
        if show_ascii:
            for c in b_slice:
                c = chr(c)
                if c.isprintable():
                    s += c
                else:
                    s += '.'
        length -= bytes_per_line
        offset += bytes_per_line
        yield s


def initialize_console():
    """Initialize the console to work with UTF-8 encoded strings.

        On windows, the console is strange and if output is redirected to a
        file, it gets even stranger. This confuses Python and even though
        PEP 528 solves the problem for interactive consoles, this does not
        help for non-interactive (which redirected streams are).

        The solution for now is to reconfigure the codecs for stdout and
        stderr to always use UTF-8 and replace unmappable characters.
    """
    if os.name == 'nt':
        if sys.stdout.encoding != 'utf-8':
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'replace')
            print('Reconfigured stdout to use utf-8 encoding.')
        if sys.stderr.encoding != 'utf-8':
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'replace')
            print('Reconfigured stderr to use utf-8 encoding.')


def iso8601_str(d: datetime,
                seconds_digits: int = 0,
                compact: bool = False,
                utc: bool = False) -> str:
    """Convert a datetime to an ISO8601 string.

        An ISO8601 compliant string is not fully defined, implementations
        have some leeway in the formatting. This function will produce various
        strings, depending on the input parameters.

        The timezone information ("±HHMM") is only present for aware datetime
        objects (e.g. datetime with tzinfo).

        The number of fractional seconds digits is given by seconds_digits. If
        zero digits are requested, the decimal point is left out (e.g.
        "2023-11-21T18:37:31"). If more than 6 digits are requested, only 6
        digits will be output because datetime objects are limited to
        microsecond resolution.

        Compact notation does not separate the different fields of the string
        (e.g. "YYYY-MM-DDTHH:MM:SS" becomes "YYYYMMDDTHHMMSS").

        UTC notation will convert the datetime into UTC. Note that if the
        datetime is not aware, Python will assume it is in localtime. Instead
        of the time zone offset, a "Z" will be appended.

        :param datetime d: Date to convert to a string.
        :param int seconds_digits: Digit of precision of the seconds.
        :param bool compact: Use separators between values if False,
            compact representation if True.
        :param bool utc: Output UTC time with 'Z' suffix instead of timezone offset.
        :return: String representation of the datetime.

        **Example**

        Given the datetime 2023-11-21T18:37:31.123456+0100 and that we are
        running in GMT-02, the following will be output:

        ===== ============== ======= ===== ===============================
        aware seconds_digits compact utc   Result
        ===== ============== ======= ===== ===============================
        Yes   0              False   False 2023-11-21T18:37:31+0100
        Yes   1              False   False 2023-11-21T18:37:31.1+0100
        Yes   6              False   False 2023-11-21T18:37:31.123456+0100
        Yes   7              False   False 2023-11-21T18:37:31.123456+0100
        No    6              False   False 2023-11-21T18:37:31.123456
        Yes   6              True    False 20231121T183731.123456+0100
        Yes   6              False   True  2023-11-21T17:37:31.123456Z
        No    6              False   True  2023-11-21T15:37:31.123456Z
        ===== ============== ======= ===== ===============================

        **Note**: non-aware and utc=True result depends on current

        .. versionadded:: 1.4.1
    """
    if utc:
        d = d.astimezone(tz=timezone.utc)
    if compact:
        s = f'{d.strftime("%Y%m%dT%H%M%S")}'
    else:
        s = f'{d.strftime("%Y-%m-%dT%H:%M:%S")}'
    if seconds_digits > 0:
        if seconds_digits > 6:
            seconds_digits = 6  # datetime is only precise to microseconds
        fractional_seconds = int(d.microsecond / 10**(6-seconds_digits))
        s += f'.{fractional_seconds:0{seconds_digits}d}'
    if utc:
        s += 'Z'
    elif d.tzinfo:
        s += f'{d.strftime("%z")}'
    return s


def logging_add_trace():
    """Add a loglevel TRACE.

        This function should be called only once.
    """
    if hasattr(logging_add_trace, "nr_calls"):
        logging_add_trace.nr_calls += 1
        logging.getLogger(__name__).warning(
            'logging_add_trace() called %d times.',
            logging_add_trace.nr_calls)
        return
    logging_add_trace.nr_calls = 1  # it doesn't exist yet, so initialize it

    if hasattr(logging, 'TRACE'):
        logging.getLogger(__name__).debug('TRACE logging already enabled.')

    # Perform function.
    logging.TRACE = 9
    logging.addLevelName(logging.TRACE, 'TRACE')

    def trace(self, message, *args, **kws):
        """Output message with level TRACE."""
        if self.isEnabledFor(logging.TRACE):
            # Logger takes its '*args' as 'args'.
            self._log(logging.TRACE, message, args, **kws)  # pylint: disable=protected-access

    logging.Logger.trace = trace


def logging_initialize(
        loglevel: int = logging.WARNING,
        log_dir_path: Path = Path('.'),
        log_file_name_format: str = '%P.log',
        log_rotation: int = 0,
        log_compression: int = 5,
        loglevel_console: int = logging.WARNING,
        loglevel_file: int = logging.DEBUG) -> logging.Logger:
    """Initialize logging and return an instance of the root logger.

        If a submodule uses :py:`logging.getLogger('somename')`, the logger will
        be a child of the root logger and inherit the settings made here.

        :param int loglevel: Loglevel of the logger. Log messages not meeting
            the level requirement are not logged.
        :param Path log_dir_path: Path of the directory containing log files.
            :py:`None` will prevent log file creation.
        :param str log_file_name_format: Format string for the log file name.
            :py:`None` will prevent log file creation.
        :param int log_rotation: How many logfiles of the same name to keep.
            If set to 0, any existing log file is overwritten. If set to >0,
            that many old log file copies (named <name>.1, <name>.2, etc.)
            are retained.
        :param int log_compression: Zlib compression level to use in compressing
            log. Level 0 is no compression, level 9 is the highest possible.
        :param int loglevel_console: Loglevel filter of the console logger.
        :param int loglevel_file: Loglevel filter of the file logger.
        :return: The root logger instance for the application.
        :rtype: logging.logger

        :note: If the :py:`log_file_name_format` contains a timestamp, log_rotation
            will only work on other log file copies with the exact same timestamp.
    """
    # Configure the root logger instance.
    global logger   # # pylint: disable=global-statement
    logger = logging.getLogger()
    logger.setLevel(loglevel)

    # Configure the console handler.
    lc = locale.getpreferredencoding()
    if lc.lower() != 'utf-8':
        locale.setlocale(locale.LC_CTYPE, 'C')
    initialize_console()
    ch = logging.StreamHandler()
    ch.setLevel(loglevel_console)
    terse_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    ch.setFormatter(terse_formatter)
    logger.addHandler(ch)
    logger.debug('Logging to console initialized.')

    if log_file_name_format is not None and log_dir_path is not None:
        log_file_name = string_from_format(log_file_name_format)
        log_file_path = log_dir_path / log_file_name
        rotate_file(log_file_name, log_dir_path, log_rotation, log_compression)

        fh = logging.FileHandler(log_file_path, encoding='utf-8', mode='w')
        fh.setLevel(loglevel_file)
        verbose_formatter = logging.Formatter('%(asctime)s %(name)-26s %(levelname)-8s %(message)s')
        fh.setFormatter(verbose_formatter)
        logger.addHandler(fh)
        logger.debug('Logging to file "%s" initialized.', log_file_path)

    if lc.lower() != 'utf-8':
        if locale.getpreferredencoding().lower() == 'utf-8':
            logger.debug('Changed encoding from "%s" to "utf-8".', lc)
        elif lc == locale.getpreferredencoding():
            logger.debug('Failed to change encoding from "%s" to "utf-8".', lc)
        else:
            logger.warning('Failed to change encoding from "%s" to "utf-8", got "%s".',
                           lc, locale.getpreferredencoding())

    return logger


def initialize_logging(args: argparse.Namespace):
    """Initialize the logging interface with the command line options
        passed through the object 'args'. An instance of the root logger is
        returned to the caller.

        If a submodule uses `logging.getLogger('somename')`, the logger will
        be a child of the root logger and inherit the settings made here.

        :param argparse.Namespace args: Namespace containing attributes used as parameters.
        :return: The root logger instance for the application.
        :rtype: logging.logger

        Namespace attributes used:
            * `args.debug` bool - Enable or disable debug mode.
            * `args.logging` str - Loglevel (e.g. CRITICAL, ERROR, etc.)
            * `args.verbose` bool - Enable or disable verbose mode.

        .. deprecated:: 1.2.0
           Use :func:`logging_initialize` and :func:`logging_add_trace()` (if
           needed) instead.
    """

    # Define a new log level 'trace'
    logging_add_trace()

    # args.loglevel contains the string value of the command line option
    # --loglevel.
    numeric_log_level = getattr(logging, args.loglevel.upper(), None)
    if not isinstance(numeric_log_level, int):
        raise ValueError(f'Invalid log level: {args.loglevel}')

    # Configure the root logger instance.
    global logger   # # pylint: disable=global-statement
    logger = logging.getLogger()
    if args.debug:
        logger.setLevel(logging.TRACE)
    else:
        logger.setLevel(numeric_log_level)

    # Create file handler only if debug mode is active.
    if args.debug:
        app_name = sys.argv[0]
        fh = logging.FileHandler(app_name + '.log', encoding='utf-8', mode='w')
        fh.setLevel(logging.TRACE)

    lc = locale.getpreferredencoding()
    if lc != 'utf-8':
        locale.setlocale(locale.LC_CTYPE, 'C')

    # Create a console handler.
    initialize_console()
    ch = logging.StreamHandler()
    ch.setLevel(numeric_log_level)

    # Create a formatter and add it to the handlers.
    terse_formatter = logging.Formatter('%(levelname)-8s %(message)s')
    ch.setFormatter(terse_formatter)
    if args.debug:
        verbose_formatter = logging.Formatter(
            '%(asctime)s %(name)-26s %(levelname)-8s %(message)s')
        fh.setFormatter(verbose_formatter)

    # Add the handlers to the logger.
    logger.addHandler(ch)
    if args.debug:
        logger.addHandler(fh)

    if args.verbose:
        logger.info('Logging initialized.')

    if lc != 'utf-8':
        if locale.getpreferredencoding() == 'utf-8':
            logger.debug('Changed encoding from "%s" to "utf-8".', lc)
        elif lc == locale.getpreferredencoding():
            logger.debug('Failed to change encoding from "%s" to "utf-8".', lc)
        else:
            logger.warning('Failed to change encoding from "%s" to "utf-8", got "%s".',
                           lc, locale.getpreferredencoding())

    logger.debug('Parsed args are: %s', args)
    logger.warning('utilities.initialize_logging() is deprecated, use utilities.logging_initialize() instead.')
    return logger


def is_power_of_two(n: int) -> bool:
    """Return True if the given number *n* is a power of two.

        :param int n: number to check
        :return: True if *n* is a power of two, False otherwise.
        :rtype: bool
    """
    return (n != 0) and ((n & (n - 1)) == 0)


def log_hexdump(fn_logger: logging.Logger,
                b: bytes,
                bytes_per_line: int = 16,
                level: int = logging.DEBUG,
                start_offset: int = 0,
                first_prefix: str = '',
                always_prefix: str = '',
                show_ascii: bool = True):
    """Log a pretty representation of the given bytes to the logger.

        ```
        first_prefix   00000000  64 65 66 67 68 69 6A 6B  @ABCDEFG
        always_prefix  00000000  64 65 66 67 68 69 6A 6B  @ABCDEFG
        ```

        :param logging.Logger fn_logger: The logger to log to.
        :param bytes b: The bytes to print.
        :param int bytes_per_line: The number of bytes per line.
        :param int level: Level for logging (e.g. CRITICAL, ERROR, .. DEBUG)
        :param int start_offset: The starting offset for the first byte.
        :param str first_prefix: A string before the offset on the first line.
        :param str always_prefix: A string that will be printed before every
            line (except the first if first_prefix was specified).
        :param bool show_ascii: Print ASCII characters after the hex dump if True.
    """
    if len(first_prefix) == 0:
        first_prefix = always_prefix
    elif len(first_prefix) > len(always_prefix):
        always_prefix += ' ' * (len(first_prefix) - len(always_prefix))
    elif len(always_prefix) > len(first_prefix):
        first_prefix += ' ' * (len(always_prefix) - len(first_prefix))
    first = True
    for line in hexdump(b,
                        bytes_per_line=bytes_per_line,
                        start_offset=start_offset,
                        offset_digits=8,
                        show_ascii=show_ascii):
        if first:
            fn_logger.log(level, '%s  %s', first_prefix, line)
            first = False
        else:
            fn_logger.log(level, '%s  %s', always_prefix, line)


def log_pp(fn_logger: logging.Logger,
           obj: Any,
           level: int = logging.DEBUG,
           indent: int = 0,
           nesting_indent: int = 1,
           max_width: int = 80,
           compact: bool = False,
           sort_dicts: bool = True):
    """Log an object formatted with pprint.pformat to a logger.
    Mutli-line output is spread to multiple log entries.

    :param logging.Logger fn_logger: Logger instance to log to.
    :param Any obj: Object to log.
    :param int level: Level for logging (e.g logging.DEBUG, logging.INFO, ...)
    :param int indent: Number of spaces to indent all entries.
    :param int nesting_indent: Additional indentation for each object nesting
        level.
    :param int max_width: Maximum width of the formatted object if `indent` is
        zero. The maximum log message length is `max_width + indent`.
    :param bool compact: True to use compact representation, False for pretty.
    :param bool sort_dicts: True to sort dictionaries before output.

    .. csv-table:: log_pp() Parameter correspondence to `pprint.PrettyPrinter <https://docs.python.org/3/library/pprint.html#pprint.PrettyPrinter>`_
        :header: "log_pp", "pprint.PrettyPrinter"
        :align: left

        "`nesting_indent`", "`indent`"
        "`max_width`", "`width`"
        "`compact`", "`compact`"
        "`sort_dicts`", "`sort_dicts`"
    """
    if not fn_logger.isEnabledFor(level):
        return
    fmt = ' ' * indent + '%s'
    for line in pformat(object=obj,
                        indent=nesting_indent,
                        width=max_width,
                        compact=compact,
                        sort_dicts=sort_dicts).splitlines():
        fn_logger.log(level, fmt, line)


def log_stacktrace(fn_logger: logging.Logger,
                   level: int = logging.DEBUG):
    """Log the current stack trace inside or outside an exception.

        :param logging.Logger fn_logger: The logger to log to.
        :param int level: Level for logging (e.g. CRITICAL, ERROR, .. DEBUG)
    """
    # Get the current exception.
    ex = sys.exc_info()[0]
    # Remove this method from the call stack.
    stack = traceback.extract_stack()[:-1]
    if ex is not None:
        # Exception is present, so remove the call of this method.
        del stack[-1]
    fn_logger.log(level, 'Traceback (most recent call last):')
    for s in traceback.format_list(stack):
        fn_logger.log(level, s)
    if ex is not None:
        fn_logger.log(level, traceback.format_exc())


def netmask_string_to_cidr(netmask: str) -> int:
    """Convert an IPv6 netmask string to a CIDR.

    :param str netmask: Netmask string to convert.
    :return: CIDR.
    :rtype: int

    Example
    -------
    .. code-block:: python

        netmask_string_to_cidr('ffff:fff0::')

    .. versionadded:: 1.5.3
    """

    # From https://stackoverflow.com/a/33533007/7083698
    bit_count = [
        0,
        0x8000,
        0xC000,
        0xE000,
        0xF000,
        0xF800,
        0xFC00,
        0xFE00,
        0xFF00,
        0xFF80,
        0xFFC0,
        0xFFE0,
        0xFFF0,
        0xFFF8,
        0xFFFC,
        0xFFFE,
        0xFFFF,
    ]  # bit_count

    count = 0
    for w in netmask.split(':'):
        if not w or int(w, 16) == 0:
            break
        count += bit_count.index(int(w, 16))

    return count


def remove_duplicates_from_list(in_list: list[Any]) -> list[Any]:
    """Remove duplicates from a list, preserving order.

        :param list[Any] in_list: The list to remove duplicates from.
        :return: A new list with the duplicates removed.
        :rtype: list[Any]
    """
    seen_entries = set()  # all entries previously seen
    return [x for x in in_list if not (x in seen_entries or seen_entries.add(x))]


def resolve_wildcards(filenames: list[str]) -> list[Path]:
    """Resolve unique Paths from a list containing wildcards.

        Item order of the input list is preserved in result.

        :param list[str] filenames: A list of filenames that may contain
             wildcards.
        :return: A list of unique Paths.
        :rtype: list[Path]

        .. versionchanged:: 1.5.2 Item order is preserved.
    """
    # Resolve wildcards.
    names = []
    for n in filenames:
        i = glob.glob(n)
        if i:
            names.extend(i)
    names = remove_duplicates_from_list(names)

    # Convert strings to paths.
    paths = [Path(n) for n in names]
    return paths


def rotate_file(file_name: str,
                file_dir: Path,
                rotation: int,
                compress_level: int = 9,
                fn_logger: logging.Logger = logging.getLogger(__name__)):
    """Rotate a (log-)file.

        The parameter rotation specifies the number of copies that will be
        retained.

        When rotating, file_name.rotation-1 is renamed to file_name.rotation
        for all values of rotation down to 1.

        The initial file (with no .rotation suffix) gains a suffix. If
        compress_level > 0, the initial file is also compressed.

        :param str file_name: Name of the log file.
        :param Path file_dir: Path to the directory containing the log file.
        :param int rotation: Number of copies to rotate. 0 to disable.
        :param int compress_level: Zlib compression level with 0 being no
            compression and 9 the highest possible.
        :param logging.Logger fn_logger: Logger used by the function.
    """
    fn_logger.debug('rotate_log(%s, %s, %d)', file_name, file_dir, rotation)
    if rotation == 0:
        fn_logger.debug('rotate_log(): nothing to rotate.')
        return

    max_rotation = rotation
    while rotation >= 0:
        if rotation == 0:
            candidate = file_dir / file_name
            if not candidate.exists():
                fn_logger.debug('rotate_log(): rotation 0 does not exists. Done.')
                return
            candidate_is_compressed = False
        else:
            # Find previously rotated candidate.
            candidate = file_dir / f'{file_name}.{rotation}'
            candidate_is_compressed = False
            if not candidate.exists():
                candidate = file_dir / f'{file_name}.{rotation}.gz'
                candidate_is_compressed = True
                if not candidate.exists():
                    fn_logger.debug('rotate_log(): rotation %d does not exist.', rotation)
                    rotation -= 1
                    continue

        # We have found a match.
        fn_logger.debug('rotate_log(): found candidate %s.', candidate)
        if rotation == 0:
            # All other rotation copies have been renamed, now the last logfile
            # must be compressed (optional) and renamed.
            compress_path = file_dir / file_name
            if compress_level > 0:
                new_name = f'{file_name}.1.gz'
                new_path = file_dir / new_name
                fn_logger.debug('rotate_log(): compress %s -> %s.', compress_path, new_path)
                with open(compress_path, 'rb') as f_in:
                    # Get the modification time of the file we are rotating
                    # so it will be stored correctly in the gzip archive.
                    statinfo = os.stat(compress_path)
                    with open(new_path, 'wb') as f_out:
                        with gzip.GzipFile(file_name,
                                           'wb',
                                           compress_level,
                                           f_out,
                                           mtime=statinfo.st_mtime) as f_zip:
                            shutil.copyfileobj(f_in, f_zip)

                fn_logger.debug('rotate_log(): unlink %s.', compress_path)
                compress_path.unlink()
            else:
                new_path = file_dir / f'{file_name}.{rotation + 1}'
                fn_logger.debug('rotate_log(): rename %s -> %s', candidate, new_path)
                candidate.rename(new_path)
        elif rotation == max_rotation:
            # We have found the maximum rotation file. Delete it to make room.
            fn_logger.debug('rotate_log(): unlinking old %s.', candidate)
            candidate.unlink()
        elif rotation > 0:
            # Rename existing rotation to next higher.
            if candidate_is_compressed:
                new_path = file_dir / f'{file_name}.{rotation + 1}.gz'
            else:
                new_path = file_dir / f'{file_name}.{rotation + 1}'
            fn_logger.debug('rotate_log(): rename %s -> %s', candidate, new_path)
            candidate.rename(new_path)
        rotation -= 1


def round_down(n: int, m: int) -> int:
    """Round the given number *n* down to the nearest multiple of *m*.

        :param int n: number to round
        :param int m: multiple to round to
        :return: n rounded down to a multiple of m.
        :rtype: int
    """
    return n & ~(m - 1)


def round_up(n: int, m: int) -> int:
    """Round the given number *n* up to the nearest multiple of *m*.

        :param int n: number to round
        :param int m: multiple to round to
        :return: n rounded up to a multiple of m.
        :rtype: int
    """
    return (n + m - 1) & ~(m - 1)


@contextlib.contextmanager
def std_open(filename: str | Path | None = None,
             mode: str = 'rt',
             encoding: str = 'utf-8',
             newline: str | None = None):
    """Open either a file or stdin/stdout for use with `with`.

        If the filename is None or '-' then stdin or stdout (depending on the
        mode) are used.
        Otherwise, the file is used. It is closed when the `with` block is done.

        If the filename ends with a well-known compression format extension,
        this compression format is used:

        .bz2
            bzip2 compressed file, uses :py:func:`bz2.open`
        .gz
            GZip compressed file, uses :py:func:`gzip.open`.
        .xz
            LZMA compressed file, uses :py:func:`lzma.open`.

        :param str|Path|None filename: A filename, Path-like, '-', or `None`.
        :param str mode: The mode to use for :func:`open`. Valid modes are:
            'rb', 'ab', 'wb', 'xb' for binary mode, or 'rt', 'at', 'wt', or 'xt'
            for text mode. The default is 'rt'.
        :param str encoding: The encoding to pass to :func:`open`. Defaults to 'utf-8'.
        :param str newline: Universal newline mode. Passed to :func:`open`.

        .. note::

            The modes 'a', 'r', 'w', and 'x' default to text mode for
            uncompressed, and to binary mode for compressed formats. I
            recommend avoiding them. Always express your programs intent
            explicitly to avoid problems.

        Example
        -------
        .. code-block:: python

            with std_open(fn, 'rt') as f:
                c = f.read()

        .. versionchanged:: 1.3.1
           Default mode changed to 'r' to minimize chances of accidental file clobbering.
        .. versionchanged:: 1.4.2
           Add parameter `newline`.
        .. versionchanged:: 1.5.1
           Add ability to read/write compressed files.
           Allow Path-like object for the filename.
    """
    format_map = {
        '.bz2': bz2.open,
        '.bzip2': bz2.open,
        '.gz': gzip.open,
        '.gzip': gzip.open,
        '.xz': lzma.open,
    }  # format_map
    open_func = open

    if not filename or filename == '-':
        if 'r' in mode:  # pylint: disable=else-if-used
            fh = sys.stdin
        else:  # 'w'
            fh = sys.stdout
    else:
        file_path = Path(filename)
        file_suffix = file_path.suffix
        if file_suffix in format_map:
            open_func = format_map[file_suffix]

        if 'b' in mode:
            fh = open_func(file_path, mode=mode)
        else:
            # Text mode allows more options than binary mode.
            fh = open_func(file_path,
                           mode=mode,
                           encoding=encoding,
                           newline=newline)

    try:
        yield fh
    finally:
        if fh is not sys.stdin and fh is not sys.stdout:
            fh.close()


def string_from_format(fmt: str, timestamp: datetime = None) -> str:
    """Given a strftime()-like format, expand into a string.

        Additional formats:
        - %P - name of the application

        :param str fmt: Format string to apply.
        :param datetime timestamp: Timestamp to format or `None` to use the current time.
        :return: Resulting string.
    """
    fmt2 = ''
    if '%P' in fmt:
        start = 0
        pos = fmt.find('%P', start)
        while pos >= 0:
            length = pos - start
            fmt2 += fmt[start:length] + Path(sys.argv[0]).stem
            start = pos + 2
            pos = fmt.find('%P', start)
        fmt2 += fmt[start:]
    else:
        fmt2 = fmt

    if timestamp is None:
        timestamp = datetime.now()
    return timestamp.strftime(fmt2)


def string_to_snake_case(string: str) -> str:
    """Convert a string to snake_case.

    :param str string: String to convert.
    :rtype str:
    :return: Converted snake_case string.

    .. seealso:: https://stackoverflow.com/a/1176023
    """
    # Edge case of an acronym followed by another word (e.g. "HTTPResponse"
    # -> "HTTP_Response") OR the more normal case of an initial lowercase word
    # followed by a capitalized word (e.g. "getResponse" -> "get_Response").
    string = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', string)
    # Replace double __ with single _ (e.g. __HTTP_Response -> _HTTP_Response).
    string = re.sub('__([A-Z])', r'_\1', string)
    # Normal case of two non-acronyms (e.g. "ResponseCode" -> "Response_Code")
    string = re.sub('([a-z0-9])([A-Z])', r'\1_\2', string)
    # Convert everything to lower case.
    return string.lower()


def true_stem(path: Path) -> str:
    """Return the true stem (e.g. the name without suffixes) of the Path.

        :param Path path: A Path object.
        :rtype: str
        :return: The final file or directory name without any suffixes.

        Example
        -------

        .. code-block:: python

            print(true_stem(Path('/var/tmp/abc.tar.gz')))
            abc

    """
    ts = path.stem
    while path.suffixes:
        ts = path.stem
        path = Path(ts)
    return ts


def wrapping_counter_delta(first: int, second: int, max_value: int) -> int:
    """Calculate the difference between two values of a wrapping counter.

    :param int first: The first counter value.
    :param int second: The second (later) counter value.
    :param int max_value: The maximum value the counter can reach plus one.
        For fixed-length integers, this is 2**<num_bits>.
    :returns: The difference between the two counter values.

    Example for a 4 bit counter (range 0..15)::

         0             0            0             0 1             1
         0             f            0             f 0             f
        |---------------|          |---------------|---------------|
           ^        ^       ===>               ^      ^
           2nd      1st                        1st    2nd

        first  = 0x0c (= 12)
        second = 0x03 (=  3)
        delta = 0x03 + 0x10 - 0x0c = 0x07
                   3 +   16 -   12 =    7

    .. versionadded:: 1.5.0
    """
    if first <= second:
        delta = second - first
    else:
        delta = second + max_value - first
    return delta


if __name__ == '__main__':
    if sys.version_info < (3, 9):
        sys.stderr.write('FATAL ERROR: Python 3.9 or later is required.\n')
        sys.exit(1)
