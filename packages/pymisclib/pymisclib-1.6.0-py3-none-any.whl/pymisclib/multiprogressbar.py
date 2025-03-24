#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2012-2022, 2023 by Christian Dönges
# SPDXID: SPDXRef-multiprogressbar-py
"""Print multiple progress bars to the console.

   The configuration of the bars is handled through a list of dictionaries.
   Each dictionary contains the parameters for a single progress bar.

   Before the bars are shown, ``prepare_bars()`` must be called to make room for
   the bars on the console.

   Each time a bar is updated, ``print_bars()`` is called to update the console
   output.

   Bar example
   -----------

   A simple example shows a bar for the entire process and a second bar for
   individual progress steps below the first bar.

   This is an example: ::

       Total |------------------------------| 0% Writing
             |███████████████---------------| 50.9% /tmp3muil9sc/0000000000000000.tmp


   .. code-block:: python

       from multiprogressbar import prepare_bars, print_bars

       config = [
           {
               'current_iteration': 0,
               'total_iterations': 5,
               'prefix': 'Total',
               'suffix': 'Writing',
               'decimals': 0,
               'bar_length': 30},
           {
               'current_iteration': 509,
               'total_iterations': 1000,
               'prefix': '     ',
               'suffix': '/tmp3muil9sc/0000000000000000.tmp',
               'decimals': 1,
               'bar_length': 30},
       ]
       prepare_bars(config)
       print_bars(config)

"""

import sys
from dataclasses import dataclass, field
from math import floor
from time import sleep

from pymisclib import ansiterminal
from pymisclib.ansiterminal import AnsiTerminal
from pymisclib.unicodechars import UC


_eighths_map = {
    0: UC.general_punctuation.em_space,
    1: UC.block_elements.left_one_eight_block,
    2: UC.block_elements.left_one_quarter_block,
    3: UC.block_elements.left_three_eights_block,
    4: UC.block_elements.left_half_block,
    5: UC.block_elements.left_five_eights_block,
    6: UC.block_elements.left_three_quarters_block,
    7: UC.block_elements.left_seven_eights_block,
    8: UC.block_elements.full_block,
}  # _eighths_map


# This is an ugly hack, but required to avoid breaking API changes.
# Remove in v2.0.
BAR_COLORS = ansiterminal.FgColor
"""Color codes for progress bars.

.. deprecated:: v1.5.0
   Use :py:data:`ansiterminal.FgColor` instead.

"""
# TODO: add when Sphinx 7.3 is available
# .. versionremoved:: v2.0.0
#   Duplicates :py:data:`ansiterminal.FgColor`.


def get_eighths_block(eighths: int) -> str:
    """Return a Unicode block character matching eighths/8.

    :param int eighths: Number from 0 to 8.
    :return: Unicode block element matching eighths/8.
    :rtype str:
    """
    if eighths < 0 or eighths > 8:
        raise ValueError('valid range 0..8')
    return _eighths_map[eighths]


@dataclass
class SingleProgressBar:
    """Representation of a single progress bar.

    A single bar consists of _prefix_ _bar_ _percentage_ _suffix_.

    .. versionchanged:: v1.5.0 Type of :py:paramref:`bar_color`
       changed to :py:class:`ansiterminal.FgColor`.

    """
    total_steps: int = 100
    """Steps required to complete progress."""
    prefix: str = ''
    """Text before the bar."""
    suffix: str = ''
    """Text after the bar."""
    bar_segments: int = 25
    """Number os segments in the bar when completed."""
    bar_color: ansiterminal.FgColor = ansiterminal.FgColor.Black
    """Color of the bar."""
    decimals: int = 0
    """Number of decimals to use in displaying the percentage completed."""
    _current_step: int = 0

    def __str__(self) -> str:
        """String representation of the bar."""
        return f'{self.prefix} {UC.box_drawings.light_vertical}'\
               f'{self.bar()}{UC.box_drawings.light_vertical} '\
               f'{self.percent_str()} {self.suffix}'

    def bar(self) -> str:
        """Return the bar only (no prefix, suffix, or percent) as a string."""
        filled_segments = floor(self.bar_segments * self.percent)
        the_bar = get_eighths_block(8) * filled_segments
        if filled_segments < self.bar_segments:
            partial_segments = floor((self.bar_segments * self.percent - filled_segments) * 8)
            the_bar += get_eighths_block(partial_segments)
        if len(the_bar) < self.bar_segments:
            the_bar += ' ' * int(self.bar_segments - len(the_bar))
        return the_bar

    def percent_str(self) -> str:
        """Return the percentage of the bar filled as a formatted string."""
        if self.decimals > 0:
            percents = f'{100 * self.percent:{4+self.decimals}.{self.decimals}f}%'
        else:
            percents = f'{100 * self.percent:3.0f}%'
        return percents

    @property
    def percent(self) -> float:
        """Degree to which the bar is filled as a number 0..1.

        :return: Fraction of the bar that is filled. Valid range [0..1].
        :rtype float:
        """
        percent = self._current_step / float(self.total_steps)
        return percent

    def color_string(self) -> str:
        """Representation of the entire bar (including pre- and suffix) with
        color code.

        :return: Formatted string.
        :rtype str:
        """
        return ansiterminal.FgColor.Black.value + self.prefix + \
            UC.box_drawings.light.vertical + \
            self.bar_color.value + \
            self.bar() + \
            ansiterminal.FgColor.Black.value + \
            UC.box_drawings.light.vertical + \
            f' {self.percent_str()} {self.suffix}'

    def print(self, color: bool = True):
        """Output the entire bar to sys.stdout.

        :param bool color: True to output_format bar with color information, False without.
        """
        if color:
            s = self.color_string()
        else:
            s = str(self)
        sys.stdout.write(f'\x1b[2K{s}')

    @property
    def current_step(self) -> int:
        """Current step of the bar on the way towards `total_steps`."""
        return self._current_step

    @current_step.setter
    def current_step(self, current_step: int):
        """Update the current_step of the bar.

        :param int current_step: The current step of the bar.
        """
        if current_step > self.total_steps:
            raise ValueError('current_step out of range')
        self._current_step = current_step


@dataclass
class MultiProgressBar:
    """Multiple SingleProgressBars on top of each other."""
    bars: list[SingleProgressBar] = field(default_factory=list)
    terminal: AnsiTerminal = field(default_factory=AnsiTerminal)

    def print(self, color: bool = True, first: bool = False):
        """Output the entire multibar to sys.stdout.

        :param bool color: True to output_format bar with color information, False without.
        """
        # cp = self.terminal.cursor_position()
        # logging.getLogger(__name__).debug('%s', cp)
        if not first:
            self.terminal.move_cursor_up(len(self.bars))
        for bar in self.bars:
            bar.print(color)
            sys.stdout.write('\n')
        sys.stdout.flush()

    @property
    def current_steps(self) -> list[int]:
        """Return a list of current bar steps.

        :return: A list of the current step for each bar.
        :rtype list[int]:
        """
        current_steps = []
        for b in self.bars:
            current_steps.append(b.current_step)
        return current_steps

    @current_steps.setter
    def current_steps(self, steps: list[int]):
        """Set the current step for all bars.

        :param list[int] steps: An integer step value for each bar.
        """
        if len(steps) > len(self.bars):
            raise ValueError('more steps than bars')
        index = 0
        for s in steps:
            bar = self.bars[index]
            bar.current_step = s
            index += 1


def print_single_bar(
        current_iteration: int,
        total_iterations: int,
        prefix: str = '',
        suffix: str = '',
        decimals: int = 1,
        bar_length: int = 80,
        bar_color: ansiterminal.FgColor = ansiterminal.FgColor.Black):
    """Output a single progress bar to stdout.

    :param int current_iteration: the current iteration
    :param int total_iterations: the total number of iterations
    :param str prefix: a string that will be output before the bar
    :param str suffix: a string that will be output after the bar
    :param int bar_length: the length of the bar in characters
    :param ansiterminal.FgColor bar_color: the color of the bar.

    .. versionchanged:: v1.5.0 Type of :py:paramref:`bar_color` changed
       to :py:class:`ansiterminal.FgColor`.

    """
    current_iteration = min(current_iteration, total_iterations)

    percents = f'{100 * (current_iteration / float(total_iterations)):.{decimals}f}'
    filled_length = int(round(bar_length * current_iteration / float(total_iterations)))
    the_bar = f'{"█" * filled_length}{"-" * (bar_length - filled_length)}'

    sys.stdout.write(
        f'\x1b[2K\r{prefix} |{bar_color.value}{the_bar}'
        f'{ansiterminal.FgColor.Black.value}| {percents}% {suffix}')


def prepare_bars(configs: list):
    """Print to prepare for the bars."""
    for c in configs:
        sys.stdout.write('\n')


def print_bars(configs: list):
    """Print progress bars."""
    # Move the cursor up to the start of the line of the first bar.
    for n in range(len(configs)):
        sys.stdout.write('\033[F')  # up

    for config in configs:
        ci = config['current_iteration']
        ti = config['total_iterations']
        prefix = config.get('prefix', '')
        suffix = config.get('suffix', '') + '\033[K\n'
        decimals = config.get('decimals', 1)
        bar_length = config.get('bar_length', 80)
        bar_color = config.get('bar_color', ansiterminal.FgColor.Black)
        print_single_bar(ci, ti, prefix, suffix, decimals, bar_length,
                         bar_color)
    sys.stdout.flush()


def demo_modern():
    """Demonstrate the modern API."""
    def demo_modern_single():
        """Demonstrate the use of a SingleProgressBar."""
        at = AnsiTerminal()
        total_steps = 7
        sb = SingleProgressBar(total_steps=total_steps * 8,
                               prefix='Progress ',
                               suffix='Example 1',
                               bar_segments=total_steps)
        sb.bar_color = ansiterminal.FgColor.Red
        for step in range(total_steps * 8 + 1):
            if step == (total_steps / 2) * 8:
                sb.bar_color = ansiterminal.FgColor.Yellow
            elif step == total_steps * 8:
                sb.bar_color = ansiterminal.FgColor.Green
            sb.current_step = step
            at.erase_line()
            sb.print(True)
            sys.stdout.write('\r')
            sys.stdout.flush()
            sleep(0.25)

    # demo_modern_single()
    # print('\nDone with Example 1')

    def demo_modern_multi():
        """Demonstrate use of MultiProgressBar."""
        at = AnsiTerminal()

        total_steps = [4, 5, 10, 100, 233]
        increments = [0.0, .2, .2, 1, 1]
        bars = [
            SingleProgressBar(total_steps=total_steps[0],
                              prefix='Total ',
                              suffix='',
                              bar_segments=total_steps[0],
                              bar_color=ansiterminal.FgColor.Blue),
            SingleProgressBar(total_steps=total_steps[1],
                              prefix='Proc1 ',
                              suffix='1',
                              bar_segments=10,
                              bar_color=ansiterminal.FgColor.Black),
            SingleProgressBar(total_steps=total_steps[2],
                              prefix='Proc2 ',
                              suffix='two',
                              bar_segments=total_steps[2],
                              bar_color=ansiterminal.FgColor.Green),
            SingleProgressBar(total_steps=total_steps[3],
                              prefix='Proc3 ',
                              suffix='III',
                              bar_segments=int(total_steps[3] / 10),
                              bar_color=ansiterminal.FgColor.BrightYellow),
            SingleProgressBar(total_steps=total_steps[4],
                              prefix='Proc4 ',
                              suffix='four',
                              bar_segments=12,
                              bar_color=ansiterminal.FgColor.Red,
                              decimals=1),
        ]
        mpb = MultiProgressBar(bars=bars, terminal=at)

        current_steps = [0.0, 0.0, 0.0, 0.0, 0.0]
        for step in range(max(total_steps) + 1):
            nr_bars_maxed = 0
            for index in range(1, len(current_steps)):
                if current_steps[index] < total_steps[index]:
                    current_steps[index] += increments[index]
                else:
                    nr_bars_maxed += 1
            current_steps[0] = nr_bars_maxed
            steps = []
            for s in current_steps:
                steps.append(int(s))
            try:
                mpb.current_steps = steps
            except ValueError:
                for c in steps:
                    print(c)
                    return
            mpb.print(color=True, first=(step == 0))
            sys.stdout.flush()
            sleep(0.25)

    demo_modern_multi()
    print('\nDone with Example 2')


def demo_classic():
    """Demonstration of how it works."""
    configs = [
        {
            'current_iteration': 0,
            'total_iterations': 5,
            'prefix': 'Total',
            'suffix': 'Writing',
            'decimals': 0,
            'bar_length': 30,
            'bar_color': ansiterminal.FgColor.Green,
        },
        {
            'current_iteration': 509,
            'total_iterations': 1000,
            'prefix': '     ',
            'suffix': '/tmp3muil9sc/0000000000000000.tmp',
            'decimals': 1,
            'bar_length': 30
        },
        {
            'current_iteration': 1,
            'total_iterations': 10,
            'bar_length': 15,
            'bar_color': ansiterminal.FgColor.BrightRed,
        },
        {
            'current_iteration': 0,
            'total_iterations': 100,
            'prefix': 'Jolly'
        },
    ]
    prepare_bars(configs)
    for i in range(100):
        print_bars(configs)
        for config in configs:
            config['current_iteration'] += 1
        sleep(.1)


def main():
    print('Modern interface')
    demo_modern()
    print('Classic interface')
    demo_classic()


if __name__ == '__main__':
    main()
