#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges
# SPDXID: SPDXRef-ringbuffer-py
"""Implementation of a fixed-size ringbuffer.

.. versionadded: 1.5.0

"""

import logging
import sys
from typing import Any

from pymisclib.utilities import wrapping_counter_delta


class BufferEmptyError(BufferError):
    """Raised when a buffer is empty and an attempt is made to read from it."""
    pass


class BufferFullError(BufferError):
    """Raised when a buffer is full and an attempt is made to write to it."""
    pass


class RingBuffer:
    """A fixed-size ringbuffer.

    New entries are added to the end of the buffer, the oldest entry is read
    first. Once the buffer has reached full capacity, the newest entry to be
    added will overwrite the oldest.

    The capacity should be chosen carefully to ensure that adding new
    entries never overtakes reading old ones (this will raise an exception).
    Simply opting for the largest possible buffer is not usually an optimal
    strategy because the entries are never freed (i.e. the buffer never shrinks
    in size), potentially consuming large amounts of memory.
    """
    def __init__(self, capacity: int,
                 logger: logging.Logger = logging.getLogger(__name__)):
        """
        :param int capacity: Maximum number of entries the buffer can hold.
        :param logging.Logger logger: Logger instance for diagnostics.
        """
        self._capacity = capacity
        self._logger = logger
        self._buffer = []
        self._last_read_offset = -1   # last read was from this offset
        self._last_write_offset = -1  # last write to this offset

    @property
    def capacity(self) -> int:
        """Capacity of the buffer."""
        return self._capacity

    @property
    def num_unread(self) -> int:
        """Number of entries that may be read from the buffer."""
        if self._last_write_offset < 0:
            # No writes have been performed, so there is no content.
            return 0
        if self._last_read_offset < 0:
            # No reads have been performed, so everything is content.
            return self._last_write_offset + 1
        # Both offsets are now [0..self._capacity[.
        delta = wrapping_counter_delta(self._last_read_offset,
                                       self._last_write_offset,
                                       self._capacity)
        return delta

    @property
    def size(self) -> int:
        """Current number of entries in the buffer."""
        return len(self._buffer)

    def add(self, entry: Any):
        """Add an entry to the buffer.

            :raises BufferFullError: if the buffer is full of unread entries.
        """
        if len(self._buffer) < self._capacity:
            self._buffer.append(entry)
            self._last_write_offset += 1
            return

        if self.num_unread >= self._capacity - 1:
            raise BufferFullError('read required')
        write_offset = (self._last_write_offset + 1) % self._capacity
        self._buffer[write_offset] = entry
        self._last_write_offset = write_offset

    def get(self) -> Any:
        """Read the oldest unread entry from the buffer.

            :raises BufferEmptyError: if the buffer contains no unread entries.
        """
        if self.num_unread == 0:
            raise BufferEmptyError('buffer is empty')
        self._last_read_offset = (self._last_read_offset + 1) % self._capacity
        value = self._buffer[self._last_read_offset]
        return value

    def get_unread(self) -> list[Any]:
        """Read all unread entries from the buffer.

            :returns list[Any]: A list of all unread entries. Empty list if
                the buffer is empty.
        """
        nu = self.num_unread
        if nu == 0:
            return []
        if nu == self._capacity:
            return self._buffer
        first_unread = (self._last_read_offset + 1) % self._capacity
        last_unread = (first_unread + nu) % self._capacity
        if last_unread >= first_unread:
            return self._buffer[first_unread:last_unread]
        return self._buffer[first_unread:] + self._buffer[:last_unread]


def main(argv: list) -> int:
    """Do something useful."""
    ring_buffer = RingBuffer(16)
    for i in range(16):
        ring_buffer.add(i)
    return 0


if __name__ == '__main__':
    if sys.version_info < (3, 9):
        print('FATAL ERROR: Python 3.9.x or later is required.')
        sys.exit(1)
    sys.exit(main(sys.argv))
