# dateutils.py
#
# Copyright (C) 2022 Katie Rust (katie@ktpanda.org)
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
# CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
# SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

'''
dateutils
=========

Simple utilities for dealing with date / time, extending the built-in datetime.
'''

import datetime
import time
import re

# Unix time epoch, as a datetime
EPOCH = datetime.datetime(1970, 1, 1, 0, 0, 0)

RX_TIME = re.compile(r'(\d{4})-(\d\d)-(\d\d)T(\d\d):(\d\d):(\d\d)(\.\d+)?(?:\+(\d\d)(?::(\d\d))?)?')

INTERVAL_SECONDS = {
    's': 1,
    'm': 60,
    'h': 3600,
    'd': 86400
}

# On systems that support it, use monotonic time
if hasattr(time, 'clock_gettime') and hasattr(time, 'CLOCK_MONOTONIC'):
    def getmtime():
        return time.clock_gettime(time.CLOCK_MONOTONIC)
else:
    getmtime = time.time

def timestamp_to_unix(t):
    '''Given a text timestamp with optional timezone offset, convert it to a UNIX timestamp.'''
    if t is None:
        return 0

    m = RX_TIME.match(t)
    if not m:
        return 0
    yr, mon, day, hr, min, sec, frac, ofshrs, ofsmin = m.groups()

    d = (datetime.datetime(int(yr), int(mon), int(day), int(hr), int(min), int(sec)) -
         datetime.timedelta(hours=int(ofshrs or 0), minutes=int(ofsmin or 0)))

    unix = (d - EPOCH).total_seconds()

    if frac:
        unix += float(frac)

    return unix

def localtime_to_unix(yy, mm, dd, h, m, s):
    '''Attempt to guess what the correct universal time is for the given local time.'''
    ut1 = time.mktime((yy, mm, dd, h, m, s, 0, 0, 0))
    lt = time.localtime(ut1)
    if lt.tm_isdst:
        return time.mktime((yy, mm, dd, h, m, s, 0, 0, 1))
    else:
        return ut1

def isotime(t):
    '''Convert a unix time to a ISO-8601 timestamp in GMT.'''
    itime = int(t)
    frac = t - itime
    txt = (EPOCH + datetime.timedelta(seconds=itime)).isoformat()
    if frac:
        txt += ('%.4f' % frac).lstrip('0')
    return txt + 'Z'

def parse_datespec(txt, today=None):
    '''Given a "date specification", return the date identified. `txt` can either be a
    full ISO date (YYYY-MM-DD), a partial (MM-DD), or a single number, which is
    interpreted as "days before today", where 0 is today, 1 is yesterday, etc. Can also be
    "t" for today or "y" for yesterday.'''

    if not today:
        today = datetime.date.today()

    if txt in ('t', '-'):
        return today
    elif txt == 'y':
        return today - datetime.timedelta(days=1)

    l = [int(p) for p in txt.split('-')]
    if len(l) == 1:
        return today - datetime.timedelta(days=l[0])

    if len(l) == 2:
        y = today.year
        m, d = l
        return datetime.date(y, m, d)

    if len(l) == 3:
        y, m, d = l
        return datetime.date(y, m, d)

    raise ValueError('invalid datespec: %r' % txt)

def parse_duration(text):
    '''Parse a duration into seconds. Duration can either be H:M:S, or something like
    '3h', '2h15m', etc.'''

    if ':' in text:
        ttime = 0
        for t in text.split(':'):
            ttime *= 60
            if t:
                ttime += int(t)
    else:
        ttime = 0
        expect_start = 0
        for m in re.finditer(r'(\d+)([dhms]|$)', text):
            if m.start() != expect_start:
                raise ValueError(f'Invalid duration: {text!r}')
            expect_start = m.end()
            ttime += int(m.group(1)) * INTERVAL_SECONDS.get(m.group(2), 1)

        if expect_start != len(text):
            raise ValueError(f'Invalid duration: {text!r}')

    return ttime

def split_time(secs):
    '''Split `secs` into hours, minutes, seconds, and fractions. It should always be the
    case that `sum(split_time(x)) == x`, barring rounding errors.'''
    seconds = int(secs)
    frac = secs - seconds
    minutes = seconds // 60
    seconds %= 60
    hours = minutes // 60
    minutes %= 60
    return hours, minutes, seconds, frac

def hms(secs, fracdigits=0, always_hours=False):
    '''Convert `secs` into HH:MM:SS.'''
    hours, mins, secs, frac = split_time(secs)
    if hours or always_hours:
        text = '%02d:%02d:%02d' % (hours, mins, secs)
    else:
        text = '%02d:%02d' % (mins, secs)

    if fracdigits:
        text += format(frac, f'.{fracdigits}f')

    return text

def prettytime(secs, sep=''):
    hours, mins, secs, frac = split_time(secs)

    parts = []
    if hours:
        parts.append(f'{hours}h')
    if mins:
        parts.append(f'{mins}m')
    if secs:
        parts.append(f'{secs}s')

    return sep.join(parts)
