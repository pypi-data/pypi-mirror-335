#!/usr/bin/env python3
# vim: fileencoding=utf8
# SPDXVersion: SPDX-2.3
# SPDX-License-Identifier: Apache-2.0
# SPDX-FileCopyrightText: © Copyright 2023 by Christian Dönges
# SPDXID: SPDXRef-test-utilities-iso8601-str-py

import unittest
from datetime import datetime, timedelta, timezone

from pymisclib.utilities import iso8601_str


class TestUtilitiesIso8601Str(unittest.TestCase):

    def setUp(self):
        self.timezones = [
            timezone(timedelta(hours=12), 'NZST'),
            timezone(timedelta(hours=1), 'CET'),
            timezone(timedelta(hours=0), 'GMT'),
            timezone(timedelta(hours=-8), 'PST'),
            timezone(timedelta(hours=-12), 'GMT+12'),
        ]

    @staticmethod
    def tz_offset_str(tz: timezone) -> str:
        """Convert a timezone offset to a string of the form "±HHMM".

            :param timezone tz: Timezone
            :rtype str:
            :return: Timezone offset as a string.
        """
        tz_offset = tz.utcoffset(None)
        tzo_hours = int(tz_offset.seconds / 3600) + tz_offset.days * 24
        tzo_minutes = int(abs((tz_offset.seconds - int(tz_offset.seconds / 3600) * 3600) / 60))
        tzo_str = f'{tzo_hours:+03d}{tzo_minutes:02d}'
        return tzo_str

    def test_compact_aware(self):
        for tz in self.timezones:
            d = datetime(2023, 11, 21, 8, 5, 31, 123456, tzinfo=tz)
            tzo_str = TestUtilitiesIso8601Str.tz_offset_str(tz)
            for digits in range(0, 7):
                s = iso8601_str(d, seconds_digits=digits, compact=True)
                if digits == 0:
                    expected = f'20231121T080531{tzo_str}'
                elif digits == 6:
                    expected = f'20231121T080531.123456{tzo_str}'
                else:
                    expected = f'20231121T080531.{"123456"[:-6+digits]:s}{tzo_str}'
                self.assertEqual(s, expected)

    def test_compact_naive(self):
        d = datetime(2023, 11, 21, 8, 5, 31, 123456)
        for digits in range(0, 7):
            s = iso8601_str(d, seconds_digits=digits, compact=True)
            if digits == 0:
                expected = '20231121T080531'
            elif digits == 6:
                expected = '20231121T080531.123456'
            else:
                expected = f'20231121T080531.{"123456"[:-6+digits]:s}'
            self.assertEqual(s, expected)

    def test_compact_utc_aware(self):
        for tz in self.timezones:
            d = datetime(2023, 11, 21, 8, 5, 31, 123456, tzinfo=tz)
            d_utc = d.astimezone(timezone.utc)
            for digits in range(0, 7):
                s = iso8601_str(d, seconds_digits=digits, compact=True, utc=True)
                if digits == 0:
                    expected = d_utc.strftime('%Y%m%dT%H%M%SZ')
                elif digits == 6:
                    expected = d_utc.strftime('%Y%m%dT%H%M%S.123456Z')
                else:
                    expected = d_utc.strftime(f'%Y%m%dT%H%M%S.{"123456"[:-6+digits]:s}Z')
                self.assertEqual(s, expected)

    def test_compact_utc_naive(self):
        d = datetime(2023, 11, 21, 8, 5, 31, 123456)
        d_utc = d.astimezone(timezone.utc)
        for digits in range(0, 7):
            s = iso8601_str(d, seconds_digits=digits, compact=True, utc=True)
            if digits == 0:
                expected = d_utc.strftime('%Y%m%dT%H%M%SZ')
            elif digits == 6:
                expected = d_utc.strftime('%Y%m%dT%H%M%S.123456Z')
            else:
                expected = d_utc.strftime(f'%Y%m%dT%H%M%S.{"123456"[:-6+digits]:s}Z')
            self.assertEqual(s, expected)

    def test_full_aware(self):
        for tz in self.timezones:
            d = datetime(2023, 11, 21, 8, 5, 31, 123456, tzinfo=tz)
            tzo_str = TestUtilitiesIso8601Str.tz_offset_str(tz)
            for digits in range(0, 7):
                s = iso8601_str(d, seconds_digits=digits, compact=False)
                if digits == 0:
                    expected = f'2023-11-21T08:05:31{tzo_str}'
                elif digits == 6:
                    expected = f'2023-11-21T08:05:31.123456{tzo_str}'
                else:
                    expected = f'2023-11-21T08:05:31.{"123456"[:-6+digits]:s}{tzo_str}'
                self.assertEqual(s, expected)

    def test_full_naive(self):
        d = datetime(2023, 11, 21, 8, 5, 31, 123456)
        for digits in range(0, 7):
            s = iso8601_str(d, seconds_digits=digits, compact=False)
            if digits == 0:
                expected = '2023-11-21T08:05:31'
            elif digits == 6:
                expected = '2023-11-21T08:05:31.123456'
            else:
                expected = f'2023-11-21T08:05:31.{"123456"[:-6+digits]:s}'
            self.assertEqual(s, expected)

    def test_full_utc_aware(self):
        for tz in self.timezones:
            d = datetime(2023, 11, 21, 8, 5, 31, 123456, tzinfo=tz)
            d_utc = d.astimezone(timezone.utc)
            for digits in range(0, 7):
                s = iso8601_str(d, seconds_digits=digits, compact=False, utc=True)
                if digits == 0:
                    expected = d_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
                elif digits == 6:
                    expected = d_utc.strftime('%Y-%m-%dT%H:%M:%S.123456Z')
                else:
                    expected = d_utc.strftime(f'%Y-%m-%dT%H:%M:%S.{"123456"[:-6+digits]:s}Z')
                self.assertEqual(s, expected)

    def test_full_utc_naive(self):
        d = datetime(2023, 11, 21, 8, 5, 31, 123456)
        d_utc = d.astimezone(timezone.utc)
        for digits in range(0, 7):
            s = iso8601_str(d, seconds_digits=digits, compact=False, utc=True)
            if digits == 0:
                expected = d_utc.strftime('%Y-%m-%dT%H:%M:%SZ')
            elif digits == 6:
                expected = d_utc.strftime('%Y-%m-%dT%H:%M:%S.123456Z')
            else:
                expected = d_utc.strftime(f'%Y-%m-%dT%H:%M:%S.{"123456"[:-6+digits]:s}Z')
            self.assertEqual(s, expected)


if __name__ == '__main__':
    unittest.main()
