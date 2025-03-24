#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2012-2022, 2023 by Christian Dönges
# SPDXID: SPDXRef-unicodechars-py
"""Define characters of the unicode character set by name.

    .. note:: The future of this module is currently unclear. It duplicates
        much of what is in :mod:`unicodedata` from the Python standard
        library. It is a huge effort to make and maintain seeing how large
        ever-growing Unicode already is.

        It may either get spun out into a separate package or made an invisible
        internal part of *pymisclib*.

        You have been warned.

    .. py:data:: UNICODE_CHARS
        :type: dict[str, str]

        A dictionary containing the name of the unicode character as the key
        and the character itself as a string.

        .. deprecated:: 1.5.0 use :mod:`unicodedata` from the Python standard
            library instead.

    .. py:data:: UC
        :type: argparse.Namespace

        A namespace containing namespaces mapped to Unicode blocks.
        The Unicode blocks contain Unicode symbols by name, the value
        is the symbol itself.

        The following blocks are currently defined:

        * arrows
        * block_elements
        * box_drawings

            * double
            * light
            * heavy

        * c0_controls
        * general_punctuation

"""
import unicodedata
from argparse import Namespace

# Dictionary of select Unicode characters, keyed by name.
UNICODE_CHARACTERS = {
    # C0 Code
    "NUL": "\x00",
    "SOH": "\x01",
    "STX": "\x02",
    "ETX": "\x03",
    "EOT": "\x04",
    "ENQ": "\x05",
    "ACK": "\x06",
    "BEL": "\x07",
    "BS": "\x08",  # Backspace
    "HT": "\x09",
    "LF": "\x0a",
    "VT": "\x0b",
    "FF": "\x0c",
    "CR": "\x0d",
    "SO": "\x0e",
    "SI": "\x0f",
    "DLE": "\x10",
    "DC1": "\x11",
    "DC2": "\x12",
    "DC3": "\x13",
    "DC4": "\x14",
    "NAK": "\x15",
    "SYN": "\x16",
    "ETB": "\x17",
    "CAN": "\x18",
    "EM": "\x19",
    "SUB": "\x1a",
    "ESC": "\x1b",
    "FS": "\x1c",
    "GS": "\x1d",
    "RS": "\x1e",
    "US": "\x1f",

    # Control Character
    "DEL": "\x7f",

    "EM SPACE": " ",  # U+2003
    # Arrows, 0x2190-21FF
    "LEFTWARDS ARROW": "←",  # U+2190
    "UPWARDS ARROW": "↑",  # U+2191
    "RIGHTWARDS ARROW": "→",  # U+2192
    "DOWNWARDS ARROW": "↓",  # U+2193
    # Unicode Box Drawing, 0x2500-0x257F
    "BOX DRAWINGS LIGHT HORIZONTAL": "─",  # U+2500
    "BOX DRAWINGS HEAVY HORIZONTAL": "━",  # U+2501
    "BOX DRAWINGS LIGHT VERTICAL": "│",  # U+2502
    "BOX DRAWINGS HEAVY VERTICAL": "┃",  # U+2503
    "BOX DRAWINGS LIGHT TRIPLE DASH HORIZONTAL": "┄",  # U+2504
    "BOX DRAWINGS HEAVY TRIPLE DASH HORIZONTAL": "┅",  # U+2505
    "BOX DRAWINGS LIGHT TRIPLE DASH VERTICAL": "┆",  # U+2506
    "BOX DRAWINGS HEAVY TRIPLE DASH VERTICAL": "┇",  # U+2507
    "BOX DRAWINGS LIGHT QUADRUPLE DASH HORIZONTAL": "┈",  # U+2508
    "BOX DRAWINGS HEAVY QUADRUPLE DASH HORIZONTAL": "┉",  # U+2509
    "BOX DRAWINGS LIGHT QUADRUPLE DASH VERTICAL": "┊",  # U+250A
    "BOX DRAWINGS HEAVY QUADRUPLE DASH VERTICAL": "┋",  # U+250B
    "BOX DRAWINGS LIGHT DOWN AND RIGHT": "┌",  # U+250C
    "BOX DRAWINGS DOWN LIGHT AND RIGHT HEAVY": "┍",  # U+250D
    "BOX DRAWINGS DOWN HEAVY AND RIGHT LIGHT": "┎",  # U+250E
    "BOX DRAWINGS HEAVY DOWN AND RIGHT": "┏",  # U+250F
    "BOX DRAWINGS LIGHT DOWN AND LEFT": "┐",  # U+2510
    "BOX DRAWINGS DOWN LIGHT AND LEFT HEAVY": "┑",  # U+2511
    "BOX DRAWINGS DOWN HEAVY AND LEFT LIGHT": "┒",  # U+2512
    "BOX DRAWINGS HEAVY DOWN AND LEFT": "┓",  # U+2513
    "BOX DRAWINGS LIGHT UP AND RIGHT": "└",  # U+2514
    "BOX DRAWINGS UP LIGHT AND RIGHT HEAVY": "┕",  # U+2515
    "BOX DRAWINGS UP HEAVY AND RIGHT LIGHT": "┖",  # U+2516
    "BOX DRAWINGS HEAVY UP AND RIGHT": "┗",  # U+2517
    "BOX DRAWINGS LIGHT UP AND LEFT": "┘",  # U+2518
    "BOX DRAWINGS UP LIGHT AND LEFT HEAVY": "┙",  # U+2519
    "BOX DRAWINGS UP HEAVY AND LEFT LIGHT": "┚",  # U+251A
    "BOX DRAWINGS HEAVY UP AND LEFT": "┛",  # U+251B
    "BOX DRAWINGS LIGHT VERTICAL AND RIGHT": "├",  # U+251C
    "BOX DRAWINGS VERTICAL LIGHT AND RIGHT HEAVY": "┝",  # U+251D
    "BOX DRAWINGS UP HEAVY AND RIGHT DOWN LIGHT": "┞",  # U+251E
    "BOX DRAWINGS DOWN HEAVY AND RIGHT UP LIGHT": "┟",  # U+251F
    "BOX DRAWINGS VERTICAL HEAVY AND RIGHT LIGHT": "┠",  # U+2520
    "BOX DRAWINGS DOWN LIGHT AND RIGHT UP HEAVY": "┡",  # U+2521
    "BOX DRAWINGS UP LIGHT AND RIGHT DOWN HEAVY": "┢",  # U+2522
    "BOX DRAWINGS HEAVY VERTICAL AND RIGHT": "┣",  # U+2523
    "BOX DRAWINGS LIGHT VERTICAL AND LEFT": "┤",  # U+2524
    "BOX DRAWINGS VERTICAL LIGHT AND LEFT HEAVY": "┥",  # U+2525
    "BOX DRAWINGS UP HEAVY AND LEFT DOWN LIGHT": "┦",  # U+2526
    "BOX DRAWINGS DOWN HEAVY AND LEFT UP LIGHT": "┧",  # U+2527
    "BOX DRAWINGS VERTICAL HEAVY AND LEFT LIGHT": "┨",  # U+2528
    "BOX DRAWINGS DOWN LIGHT AND LEFT UP HEAVY": "┩",  # U+2529
    "BOX DRAWINGS UP LIGHT AND LEFT DOWN HEAVY": "┪",  # U+252A
    "BOX DRAWINGS HEAVY VERTICAL AND LEFT": "┫",  # U+252B
    "BOX DRAWINGS LIGHT DOWN AND HORIZONTAL": "┬",  # U+252C
    "BOX DRAWINGS LEFT HEAVY AND RIGHT DOWN LIGHT": "┭",  # U+252D
    "BOX DRAWINGS RIGHT HEAVY AND LEFT DOWN LIGHT": "┮",  # U+252E
    "BOX DRAWINGS DOWN LIGHT AND HORIZONTAL HEAVY": "┯",  # U+252F
    "BOX DRAWINGS DOWN HEAVY AND HORIZONTAL LIGHT": "┰",  # U+2530
    "BOX DRAWINGS RIGHT LIGHT AND LEFT DOWN HEAVY": "┱",  # U+2531
    "BOX DRAWINGS LEFT LIGHT AND RIGHT DOWN HEAVY": "┲",  # U+2532
    "BOX DRAWINGS HEAVY DOWN AND HORIZONTAL": "┳",  # U+2533
    "BOX DRAWINGS LIGHT UP AND HORIZONTAL": "┴",  # U+2534
    "BOX DRAWINGS LEFT HEAVY AND RIGHT UP LIGHT": "┵",  # U+2535
    "BOX DRAWINGS RIGHT HEAVY AND LEFT UP LIGHT": "┶",  # U+2536
    "BOX DRAWINGS UP LIGHT AND HORIZONTAL HEAVY": "┷",  # U+2537
    "BOX DRAWINGS UP HEAVY AND HORIZONTAL LIGHT": "┸",  # U+2538
    "BOX DRAWINGS RIGHT LIGHT AND LEFT UP HEAVY": "┹",  # U+2539
    "BOX DRAWINGS LEFT LIGHT AND RIGHT UP HEAVY": "┺",  # U+253A
    "BOX DRAWINGS HEAVY UP AND HORIZONTAL": "┻",  # U+253B
    "BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL": "┼",  # U+253C
    "BOX DRAWINGS LEFT HEAVY AND RIGHT VERTICAL LIGHT": "┽",  # U+253D
    "BOX DRAWINGS RIGHT HEAVY AND LEFT VERTICAL LIGHT": "┾",  # U+253E
    "BOX DRAWINGS VERTICAL LIGHT AND HORIZONTAL HEAVY": "┿",  # U+253F
    "BOX DRAWINGS UP HEAVY AND DOWN HORIZONTAL LIGHT": "╀",  # U+2540
    "BOX DRAWINGS DOWN HEAVY AND UP HORIZONTAL LIGHT": "╁",  # U+2541
    "BOX DRAWINGS VERTICAL HEAVY AND HORIZONTAL LIGHT": "╂",  # U+2542
    "BOX DRAWINGS LEFT UP HEAVY AND RIGHT DOWN LIGHT": "╃",  # U+2543
    "BOX DRAWINGS RIGHT UP HEAVY AND LEFT DOWN LIGHT": "╄",  # U+2544
    "BOX DRAWINGS LEFT DOWN HEAVY AND RIGHT UP LIGHT": "╅",  # U+2545
    "BOX DRAWINGS RIGHT DOWN HEAVY AND LEFT UP LIGHT": "╆",  # U+2546
    "BOX DRAWINGS DOWN LIGHT AND UP HORIZONTAL HEAVY": "╇",  # U+2547
    "BOX DRAWINGS UP LIGHT AND DOWN HORIZONTAL HEAVY": "╈",  # U+2548
    "BOX DRAWINGS RIGHT LIGHT AND LEFT VERTICAL HEAVY": "╉",  # U+2549
    "BOX DRAWINGS LEFT LIGHT AND RIGHT VERTICAL HEAVY": "╊",  # U+254A
    "BOX DRAWINGS HEAVY VERTICAL AND HORIZONTAL": "╋",  # U+254B
    "BOX DRAWINGS LIGHT DOUBLE DASH HORIZONTAL": "╌",  # U+254C
    "BOX DRAWINGS HEAVY DOUBLE DASH HORIZONTAL": "╍",  # U+254D
    "BOX DRAWINGS LIGHT DOUBLE DASH VERTICAL": "╎",  # U+254E
    "BOX DRAWINGS HEAVY DOUBLE DASH VERTICAL": "╏",  # U+254F
    "BOX DRAWINGS DOUBLE HORIZONTAL": "═",  # U+2550
    "BOX DRAWINGS DOUBLE VERTICAL": "║",  # U+2551
    "BOX DRAWINGS DOWN SINGLE AND RIGHT DOUBLE": "╒",  # U+2552
    "BOX DRAWINGS DOWN DOUBLE AND RIGHT SINGLE": "╓",  # U+2553
    "BOX DRAWINGS DOUBLE DOWN AND RIGHT": "╔",  # U+2554
    "BOX DRAWINGS DOWN SINGLE AND LEFT DOUBLE": "╕",  # U+2555
    "BOX DRAWINGS DOWN DOUBLE AND LEFT SINGLE": "╖",  # U+2556
    "BOX DRAWINGS DOUBLE DOWN AND LEFT": "╗",  # U+2557
    "BOX DRAWINGS UP SINGLE AND RIGHT DOUBLE": "╘",  # U+2558
    "BOX DRAWINGS UP DOUBLE AND RIGHT SINGLE": "╙",  # U+2559
    "BOX DRAWINGS DOUBLE UP AND RIGHT": "╚",  # U+255A
    "BOX DRAWINGS UP SINGLE AND LEFT DOUBLE": "╛",  # U+255B
    "BOX DRAWINGS UP DOUBLE AND LEFT SINGLE": "╜",  # U+255C
    "BOX DRAWINGS DOUBLE UP AND LEFT": "╝",  # U+255D
    "BOX DRAWINGS VERTICAL SINGLE AND RIGHT DOUBLE": "╞",  # U+255E
    "BOX DRAWINGS VERTICAL DOUBLE AND RIGHT SINGLE": "╟",  # U+255F
    "BOX DRAWINGS DOUBLE VERTICAL AND RIGHT": "╠",  # U+2560
    "BOX DRAWINGS VERTICAL SINGLE AND LEFT DOUBLE": "╡",  # U+2561
    "BOX DRAWINGS VERTICAL DOUBLE AND LEFT SINGLE": "╢",  # U+2562
    "BOX DRAWINGS DOUBLE VERTICAL AND LEFT": "╣",  # U+2563
    "BOX DRAWINGS DOWN SINGLE AND HORIZONTAL DOUBLE": "╤",  # U+2564
    "BOX DRAWINGS DOWN DOUBLE AND HORIZONTAL SINGLE": "╥",  # U+2565
    "BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL": "╦",  # U+2566
    "BOX DRAWINGS UP SINGLE AND HORIZONTAL DOUBLE": "╧",  # U+2567
    "BOX DRAWINGS UP DOUBLE AND HORIZONTAL SINGLE": "╨",  # U+2568
    "BOX DRAWINGS DOUBLE UP AND HORIZONTAL": "╩",  # U+2569
    "BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE": "╪",  # U+256A
    "BOX DRAWINGS VERTICAL DOUBLE AND HORIZONTAL SINGLE": "╫",  # U+256B
    "BOX DRAWINGS DOUBLE VERTICAL AND HORIZONTAL": "╬",  # U+256C
    "BOX DRAWINGS LIGHT ARC DOWN AND RIGHT": "╭",  # U+256D
    "BOX DRAWINGS LIGHT ARC DOWN AND LEFT": "╮",  # U+256E
    "BOX DRAWINGS LIGHT ARC UP AND LEFT": "╯",  # U+256F
    "BOX DRAWINGS LIGHT ARC UP AND RIGHT": "╰",  # U+2570
    "BOX DRAWINGS LIGHT DIAGONAL UPPER RIGHT TO LOWER LEFT": "╱",  # U+2571
    "BOX DRAWINGS LIGHT DIAGONAL UPPER LEFT TO LOWER RIGHT": "╲",  # U+2572
    "BOX DRAWINGS LIGHT DIAGONAL CROSS": "╳",  # U+2573
    "BOX DRAWINGS LIGHT LEFT": "╴",  # U+2574
    "BOX DRAWINGS LIGHT UP": "╵",  # U+2575
    "BOX DRAWINGS LIGHT RIGHT": "╶",  # U+2576
    "BOX DRAWINGS LIGHT DOWN": "╷",  # U+2577
    "BOX DRAWINGS HEAVY LEFT": "╸",  # U+2578
    "BOX DRAWINGS HEAVY UP": "╹",  # U+2579
    "BOX DRAWINGS HEAVY RIGHT": "╺",  # U+257A
    "BOX DRAWINGS HEAVY DOWN": "╻",  # U+257B
    "BOX DRAWINGS LIGHT LEFT AND HEAVY RIGHT": "╼",  # U+257C
    "BOX DRAWINGS LIGHT UP AND HEAVY DOWN": "╽",  # U+257D
    "BOX DRAWINGS HEAVY LEFT AND LIGHT RIGHT": "╾",  # U+257E
    "BOX DRAWINGS HEAVY UP AND LIGHT DOWN": "╿",  # U+257F
    # Unicode Block Elements, 0x2580 - 0x259F
    "FULL BLOCK": "█",  # U+2588
    "LEFT SEVEN EIGHTS BLOCK": "▉",  # U+2589
    "LEFT THREE QUARTERS BLOCK": "▊",  # U+258A
    "LEFT FIVE EIGHTS BLOCK": "▋",  # U+258B
    "LEFT HALF BLOCK": "▌",  # U+258C
    "LEFT THREE EIGHTS BLOCK": "▍",  # U+258D
    "LEFT ONE QUARTER BLOCK": "▎",  # U+258E
    "LEFT ONE EIGHT BLOCK": "▏",  # U+258F
    "LIGHT SHADE": "░",  # U+2591
    "MEDIUM SHADE": "▒",  # U+2592
    "DARK SHADE": "▓",  # U+2593
}  # UNICODE_CHARACTERS

# A namespace containing namespaces mapped to Unicode blocks.
# The Unicode blocks contain Unicode symbols by name, the value
# is the symbol itself.
UC = Namespace(
    c0_controls=Namespace(
        nul=unicodedata.lookup('NUL'),
    ), # c0_controls
    general_punctuation=Namespace(
        em_space=unicodedata.lookup('EM SPACE'),
    ),  # general_punctuation
    arrows=Namespace(
        leftwards_arrow=unicodedata.lookup('LEFTWARDS ARROW'),
        upwards_arrow=unicodedata.lookup('UPWARDS ARROW'),
        rightwards_arrow=unicodedata.lookup('RIGHTWARDS ARROW'),
        downwards_arrow=unicodedata.lookup('DOWNWARDS ARROW'),
    ),  # arrows
    box_drawings=Namespace(
        double=Namespace(
            down_and_horizontal=unicodedata.lookup('BOX DRAWINGS DOUBLE DOWN AND HORIZONTAL'),
            down_and_left=unicodedata.lookup('BOX DRAWINGS DOUBLE DOWN AND LEFT'),
            down_and_right=unicodedata.lookup('BOX DRAWINGS DOUBLE DOWN AND RIGHT'),
            horizontal=unicodedata.lookup('BOX DRAWINGS DOUBLE HORIZONTAL'),
            up_and_horizontal=unicodedata.lookup('BOX DRAWINGS DOUBLE UP AND HORIZONTAL'),
            up_and_left=unicodedata.lookup('BOX DRAWINGS DOUBLE UP AND LEFT'),
            up_and_right=unicodedata.lookup('BOX DRAWINGS DOUBLE UP AND RIGHT'),
            vertical=unicodedata.lookup('BOX DRAWINGS DOUBLE VERTICAL'),
            vertical_and_horizontal=unicodedata.lookup('BOX DRAWINGS DOUBLE VERTICAL AND HORIZONTAL'),
            vertical_and_left=unicodedata.lookup('BOX DRAWINGS DOUBLE VERTICAL AND LEFT'),
            vertical_and_right=unicodedata.lookup('BOX DRAWINGS DOUBLE VERTICAL AND RIGHT'),
        ),  # double
        light=Namespace(
            down_and_horizontal=unicodedata.lookup('BOX DRAWINGS LIGHT DOWN AND HORIZONTAL'),
            down_and_left=unicodedata.lookup('BOX DRAWINGS LIGHT DOWN AND LEFT'),
            down_and_right=unicodedata.lookup('BOX DRAWINGS LIGHT DOWN AND RIGHT'),
            horizontal=unicodedata.lookup('BOX DRAWINGS LIGHT HORIZONTAL'),
            up_and_horizontal=unicodedata.lookup('BOX DRAWINGS LIGHT UP AND HORIZONTAL'),
            up_and_left=unicodedata.lookup('BOX DRAWINGS LIGHT UP AND LEFT'),
            up_and_right=unicodedata.lookup('BOX DRAWINGS LIGHT UP AND RIGHT'),
            vertical=unicodedata.lookup('BOX DRAWINGS LIGHT VERTICAL'),
            vertical_and_horizontal=unicodedata.lookup('BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL'),
            vertical_and_left=unicodedata.lookup('BOX DRAWINGS LIGHT VERTICAL AND LEFT'),
            vertical_and_right=unicodedata.lookup('BOX DRAWINGS LIGHT VERTICAL AND RIGHT'),
        ),  # light
        heavy=Namespace(
            down_and_horizontal=unicodedata.lookup('BOX DRAWINGS HEAVY DOWN AND HORIZONTAL'),
            down_and_left=unicodedata.lookup('BOX DRAWINGS HEAVY DOWN AND LEFT'),
            down_and_right=unicodedata.lookup('BOX DRAWINGS HEAVY DOWN AND RIGHT'),
            horizontal=unicodedata.lookup('BOX DRAWINGS HEAVY HORIZONTAL'),
            up_and_horizontal=unicodedata.lookup('BOX DRAWINGS HEAVY UP AND HORIZONTAL'),
            up_and_left=unicodedata.lookup('BOX DRAWINGS HEAVY UP AND LEFT'),
            up_and_right=unicodedata.lookup('BOX DRAWINGS HEAVY UP AND RIGHT'),
            vertical=unicodedata.lookup('BOX DRAWINGS HEAVY VERTICAL'),
            vertical_and_horizontal=unicodedata.lookup('BOX DRAWINGS HEAVY VERTICAL AND HORIZONTAL'),
            vertical_and_left=unicodedata.lookup('BOX DRAWINGS HEAVY VERTICAL AND LEFT'),
            vertical_and_right=unicodedata.lookup('BOX DRAWINGS HEAVY VERTICAL AND RIGHT'),
        ),  # heavy
    ),  # box_drawings
    block_elements=Namespace(
        full_block=unicodedata.lookup('FULL BLOCK'),
        left_seven_eights_block=unicodedata.lookup('LEFT SEVEN EIGHTHS BLOCK'),
        left_three_quarters_block=unicodedata.lookup('LEFT THREE QUARTERS BLOCK'),
        left_five_eights_block=unicodedata.lookup('LEFT FIVE EIGHTHS BLOCK'),
        left_half_block=unicodedata.lookup('LEFT HALF BLOCK'),
        left_three_eights_block=unicodedata.lookup('LEFT THREE EIGHTHS BLOCK'),
        left_one_quarter_block=unicodedata.lookup('LEFT ONE QUARTER BLOCK'),
        left_one_eight_block=unicodedata.lookup('LEFT ONE EIGHTH BLOCK'),
        light_shade=unicodedata.lookup('LIGHT SHADE'),
        medium_shade=unicodedata.lookup('MEDIUM SHADE'),
        dark_shade=unicodedata.lookup('DARK SHADE'),
    ),  # block_elements
)  # UC
