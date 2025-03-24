#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2024 by Christian Dönges
# SPDXID: SPDXRef-test-ringbuffer-py

import unittest


from pymisclib.ringbuffer import BufferEmptyError, BufferFullError, RingBuffer

class TestRingBuffer(unittest.TestCase):

    def setUp(self):
        self.capacity = 16
        self.ring_buffer = RingBuffer(self.capacity)

    def test_empty(self):
        """Test behavior of empty ring buffer."""
        self.assertEqual(self.capacity, self.ring_buffer.capacity)
        self.assertEqual(0, self.ring_buffer.size)
        self.assertEqual(0, self.ring_buffer.num_unread)
        with self.assertRaises(BufferEmptyError):
            self.ring_buffer.get()
        unread = self.ring_buffer.get_unread()
        self.assertEqual(0, len(unread))

    def test_full(self):
        """Test behavior of full ring buffer."""
        for i in range(self.capacity):
            self.ring_buffer.add(i)
        self.assertEqual(self.capacity, self.ring_buffer.capacity)
        self.assertEqual(self.capacity, self.ring_buffer.size)
        self.assertEqual(self.capacity, self.ring_buffer.num_unread)
        with self.assertRaises(BufferFullError):
            self.ring_buffer.add(self.capacity + 1)
        unread = self.ring_buffer.get_unread()
        self.assertEqual(self.capacity, len(unread))
        for i in range(self.capacity):
            self.assertEqual(i, unread[i])

    def test_add_one(self):
        """Add one item to ring buffer."""
        self.ring_buffer.add(1)
        self.assertEqual(self.capacity, self.ring_buffer.capacity)
        self.assertEqual(1, self.ring_buffer.size)
        self.assertEqual(1, self.ring_buffer.num_unread)
        unread = self.ring_buffer.get_unread()
        self.assertEqual(1, len(unread))
        self.assertEqual(1, unread[0])

    def test_get_one(self):
        """Get one item from ring buffer."""
        self.ring_buffer.add(123)
        self.assertEqual(123, self.ring_buffer.get())
        self.assertEqual(self.capacity, self.ring_buffer.capacity)
        self.assertEqual(1, self.ring_buffer.size)
        self.assertEqual(0, self.ring_buffer.num_unread)
        unread = self.ring_buffer.get_unread()
        self.assertEqual(0, len(unread))

    def test_add_get(self):
        for i in range(self.capacity * 3 + 1):
            val = str(i)
            self.ring_buffer.add(val)
            self.assertEqual(min(self.capacity, i + 1), self.ring_buffer.size)
            self.assertEqual(1, self.ring_buffer.num_unread)
            self.assertEqual(val, self.ring_buffer.get())
            self.assertEqual(min(self.capacity, i + 1), self.ring_buffer.size)
            self.assertEqual(0, self.ring_buffer.num_unread)
        self.assertEqual(self.capacity, self.ring_buffer.capacity)

    def test_add_overflow(self):
        """Add more items than are read from the ring buffer."""
        for i in range(0, (self.capacity - 2) * 2, 2):
            iteration = int(i / 2) + 1
            self.ring_buffer.add(i)
            self.ring_buffer.add(i + 1)
            val = self.ring_buffer.get()
            self.assertEqual(iteration - 1, val)
            self.assertEqual(min(self.capacity, iteration * 2), self.ring_buffer.size)
            self.assertEqual(iteration, self.ring_buffer.num_unread)
            unread = self.ring_buffer.get_unread()
            self.assertEqual(iteration, len(unread))
            for u in range(i + 1, i + 1 - iteration, -1):
                self.assertEqual(unread.pop(), u)
        i = (self.capacity - 2) * 2
        self.ring_buffer.add(i)
        self.assertEqual(self.capacity - 1, self.ring_buffer.num_unread)
        with self.assertRaises(BufferFullError):
            self.ring_buffer.add(i + 1)

    def test_get_underflow(self):
        """Read more items than are added to the ring buffer."""
        end1 = (self.capacity - 2) * 2
        for i in range(0, end1, 2):
            iteration = int(i / 2) + 1
            self.ring_buffer.add(i)
            self.ring_buffer.add(i + 1)
            val = self.ring_buffer.get()
            self.assertEqual(iteration - 1, val)
            self.assertEqual(min(self.capacity, iteration * 2), self.ring_buffer.size)
            self.assertEqual(iteration, self.ring_buffer.num_unread)
            unread = self.ring_buffer.get_unread()
            self.assertEqual(self.ring_buffer.num_unread, len(unread))
        self.ring_buffer.add(end1)
        self.assertEqual(self.capacity - 1, self.ring_buffer.num_unread)
        num_iterations = self.ring_buffer.num_unread - 1
        for i in range(num_iterations):
            self.ring_buffer.get()
            self.ring_buffer.get()
            self.ring_buffer.add(end1 + i + 1)
            self.assertEqual(num_iterations - i, self.ring_buffer.num_unread)
            unread = self.ring_buffer.get_unread()
            self.assertEqual(self.ring_buffer.num_unread, len(unread))
            for u in range(end1 + i + 1, end1 + i + 1 - len(unread), -1):
                self.assertEqual(u, unread.pop())
        self.assertEqual(1, self.ring_buffer.num_unread)
        self.ring_buffer.get()
        self.assertEqual(0, self.ring_buffer.num_unread)
        with self.assertRaises(BufferEmptyError):
            self.ring_buffer.get()


if __name__ == '__main__':
    unittest.main()
