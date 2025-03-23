# textcolor.py
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
ttyutil
=======

Utilities for controlling Posix TTY devices and reading raw input.
'''

import sys
import os
import re
import atexit
import signal
import array
import time
import select
import asyncio

# Only import these if they are available
try:
    import termios
    import fcntl
except ImportError:
    termios = None
    fcntl = None

from collections import deque
from contextlib import contextmanager

from ktpanda import vt100 as vt
from ktpanda.dateutils import getmtime

RX_KEY_SEQ = re.compile(r'''
  (\x1b?)  # Pre escape character - key pressed with alt

  (
    \x1b [\[ON] [\?0-9;]* (?:(?=\x1b)|[^\?0-9;]) # Normal VT100 escape sequence
    |
    [^\x1b\[ON] # Other non-escape character
    |
    \A[\[ON]
  )
''', re.X | re.S)

# If the entire buffer matches this, wait for `esctime` before returning
RX_PARTIAL = re.compile(r'''
  ^ \x1b \x1b? [ON\[]? $
''', re.X | re.S)

_output = sys.stderr
def putstr(*strs):
    for s in strs:
        _output.write(str(s))
    _output.flush()

def putline(*strs):
    putstr(vt.CLEAR, *strs)

def utf8_truncated(bstr):
    '''Returns True if `bstr` ends with a truncated UTF8 multi-byte sequence.'''
    pos = len(bstr) - 1
    mbcount = 0
    while pos >= 0 and 0x80 <= bstr[pos] <= 0xBF:
        pos -= 1
        mbcount += 1

    if pos < 0:
        return False

    last = bstr[pos]
    if 0xC2 <= last <= 0xDF and mbcount < 1:
        return True

    if 0xE0 <= last < 0xEF and mbcount < 2:
        return True

    if 0xF0 <= last < 0xF7 and mbcount < 3:
        return True

    return False

if termios:
    class _terminfo:
        def __init__(self):
            self.winchcount = 0
            self.w = 80
            self.h = 25
            self.fd = 0

        def _check(self, fd):
            if not os.isatty(fd):
                return False

            try:
                tmpbuf = array.array('H', (self.w, self.h))
                fcntl.ioctl(fd, termios.TIOCGWINSZ, tmpbuf)
                self.h, self.w = tmpbuf
                self.fd = fd
                return True
            except EnvironmentError:
                return False

        def __getitem__(self, item):
            if item == 0:
                return self.w
            if item == 1:
                return self.h
            raise IndexError

        def __str__(self):
            return '%dx%d' % (self.w, self.h)

        def check(self):
            for fd in (1, 2, 0):
                if self._check(fd):
                    return True
            return False

    terminfo = _terminfo()
    terminfo.check()
    initialized = False

    def sigwinch(sig, frame):
        terminfo.winchcount += 1
        terminfo.check()

    def cleanterm():
        putstr(vt.NORM, vt.BGDEFAULT, vt.WRAPON, vt.CURSON)

    def init():
        global initialized
        if not initialized:
            initialized = True
            atexit.register(cleanterm)
            signal.signal(signal.SIGWINCH, sigwinch)


    class TermAttr(object):
        def __init__(self, seq):
            self.params = list(seq)

        def copy(self):
            return TermAttr(self.params)

        def set(self, fd, when=termios.TCSANOW):
            termios.tcsetattr(fd, when, self.params)


    def tcgetattr(fd=None):
        return TermAttr(termios.tcgetattr(fd))

    def tcsetattr(fd, tio, when=termios.TCSANOW):
        if isinstance(tio, TermAttr):
            tio.set(fd, when)
        else:
            termios.tcsetattr(fd, when, tio)

    class AttributeContextManager:
        _attrs = []

        def __init__(self, fd=None):
            if fd is None:
                fd = terminfo.fd
            self.fd = fd
            tio = tcgetattr(fd)
            for k, v in self._attrs:
                setattr(self, k, getattr(tio, k))
                setattr(tio, k, v)
            tio.set(fd)

        def __enter__(self):
            pass

        def __exit__(self, typ, val, tb):
            tio = tcgetattr(self.fd)
            for k, _ in self._attrs:
                setattr(tio, k, getattr(self, k))
            tio.set(self.fd)

    class EchoOff(AttributeContextManager):
        _attrs = [('echo', False)]

    class RawMode(AttributeContextManager):
        _attrs = [('echo', False),
                  ('icanon', False),
                  ('vmin', 1),
                  ('vtime', 1)]

    def _setup_termattr():
        def get_shift(val):
            shift = 0
            while val:
                if val == 1:
                    return None

                if val & 1:
                    return shift
                shift += 1
                val >>= 1

        def idx_prop(idx):
            def get(self):
                return self.params[idx]

            def set(self, val):
                self.params[idx] = val

            return property(get, set)

        def cc_prop(idx):
            def get(self):
                return self.params[6][idx]

            def set(self, val):
                self.params[6][idx] = val

            return property(get, set)

        def flag_prop_bool(idx, bit):
            def get(self):
                return bool(self.params[idx] & bit)

            def set(self, val):
                if val:
                    self.params[idx] = self.params[idx] | bit
                else:
                    self.params[idx] = self.params[idx] & ~bit

            return property(get, set)

        def flag_prop_num(idx, mask, shift):
            def get(self):
                return (self.params[idx] & mask) >> shift

            def set(self, val):
                val = int(val)
                self.params[idx] = (self.params[idx] & ~mask) | ((val << shift) & mask)

            return property(get, set)

        def put_flags(idx, *flags):
            for f in flags:
                try:
                    bit = getattr(termios, f.upper())
                    shift = get_shift(bit)
                    if shift is None:
                        setattr(TermAttr, f, flag_prop_bool(idx, bit))
                    else:
                        setattr(TermAttr, f, flag_prop_num(idx, bit, shift))
                except AttributeError:
                    pass

        def put_cc(*names):
            for name in names:
                try:
                    idx = getattr(termios, name.upper())
                    setattr(TermAttr, name, cc_prop(idx))
                except AttributeError:
                    pass


        put_flags(0, 'ignbrk', 'brkint', 'ignpar', 'parmrk', 'inpck',
                  'istrip', 'inlcr', 'igncr', 'icrnl', 'iuclc', 'ixon', 'ixany',
                  'ixoff', 'imaxbel', 'iutf8')

        put_flags(1, 'opost', 'olcuc', 'onlcr', 'ocrnl', 'onocr', 'onlret',
                  'ofill', 'ofdel', 'nldly', 'crdly', 'tabdly', 'bsdly', 'vtdly',
                   'ffdly')

        put_flags(2, 'cbaud', 'cbaudex', 'cbaud', 'csize', 'cstopb', 'cread',
                  'parenb', 'parodd', 'hupcl', 'clocal', 'loblk', 'cibaud', 'cbaud',
                  'ibshift', 'cmspar', 'crtscts')

        put_flags(3, 'isig', 'icanon', 'xcase', 'echo', 'echoe', 'echok',
                  'echonl', 'echoctl', 'echoprt', 'echoke', 'defecho', 'flusho',
                  'noflsh', 'sigsusp', 'tostop', 'sigttou', 'pendin',
                  'iexten')

        put_cc('vintr', 'vquit', 'verase', 'vkill', 'veof', 'vmin',
               'veol', 'vtime', 'veol2', 'vswtch', 'vstart', 'vstop',
               'vsusp', 'vdsusp', 'vlnext', 'vwerase', 'vreprint',
               'vdiscard', 'vstatus', 'vmin')

        TermAttr.iflag  = idx_prop(0)
        TermAttr.oflag  = idx_prop(1)
        TermAttr.cflag  = idx_prop(2)
        TermAttr.lflag  = idx_prop(3)
        TermAttr.ispeed = idx_prop(4)
        TermAttr.ospeed = idx_prop(5)
        TermAttr.cc     = idx_prop(6)

    _setup_termattr()
    del _setup_termattr


    def _progressbar(size, val):
        return

    class TTYInput:
        '''Class for managing raw keyboard input for a TTY. Can also switch to the
        alternate screen while running.
        '''

        def __init__(self, fd=None, closefd=False, altscr=False, hidecurs=False,
                     altkeypad=False, signals=False, esc_detect_time=0.1, timefunc=time.time):
            if fd is None:
                fd = terminfo.fd

            self.altscr = altscr
            self.hidecurs = hidecurs
            self.altkeypad = altkeypad
            self.signals = signals
            self.orig_terminfo = None
            self.new_terminfo = None
            self.esc_detect_time = esc_detect_time
            self.closefd = closefd
            self.fd = fd
            self.buf = ''
            self.rawbuf = bytearray()
            self.timefunc = timefunc
            self.esctime = None

            vtcodes_active = ''
            vtcodes_inactive = ''
            if altscr:
                vtcodes_active += vt.ALTSCRON
                vtcodes_inactive += vt.ALTSCROFF

            if hidecurs:
                vtcodes_active += vt.CURSOFF
                vtcodes_inactive += vt.CURSON

            if altkeypad:
                vtcodes_active += vt.KPON
                vtcodes_inactive += vt.KPOFF

            self._vtcodes_active = vtcodes_active
            self._vtcodes_inactive = vtcodes_inactive

        def fileno(self):
            return self.fd

        def close(self):
            if self.fd is not None:
                self.set_inactive()
                self.orig_terminfo = None
                if self.closefd:
                    os.close(self.fd)
                self.fd = None

        def set_active(self):
            tcsetattr(self.fd, self.new_terminfo)
            if self._vtcodes_inactive:
                putstr(self._vtcodes_active)

        def set_inactive(self):
            tcsetattr(self.fd, self.orig_terminfo)
            if self._vtcodes_inactive:
                putstr(self._vtcodes_inactive)

        def __enter__(self):
            self.orig_terminfo = tcgetattr(self.fd)
            nta = self.new_terminfo = self.orig_terminfo.copy()
            nta.echo = False
            nta.icanon = False
            nta.isig = self.signals
            nta.ixon = self.signals
            nta.vmin = 1
            nta.vtime = 1
            self.set_active()

            return self

        def __exit__(self, etype, evalue, etraceback):
            self.close()

        def restore_terminfo(self):
            tcsetattr(self.fd, self.new_terminfo)

        @contextmanager
        def disable(self):
            '''Calls set_inactive, ensuring that set_active is called afterward'''
            try:
                self.set_inactive()
                yield
            finally:
                self.set_active()

        def _check_read_key(self):
            if RX_PARTIAL.fullmatch(self.buf):
                ctime = self.timefunc()
                if self.esctime:
                    if ctime > self.esctime:
                        rv = self.buf
                        self.buf = ''
                        return rv
                else:
                    self.esctime = ctime + self.esc_detect_time
            else:
                m = RX_KEY_SEQ.match(self.buf)
                if m:
                    self.buf = self.buf[m.end():]
                    return m.group(0)

            return None

        def feed_bytes(self, data):
            self.rawbuf.extend(data)
            if not utf8_truncated(self.rawbuf):
                self.buf += self.rawbuf.decode('utf8', 'surrogateescape')
                self.rawbuf.clear()


        def readkey(self, endtime=None):
            '''Read a key from the terminal.'''
            allow_exit = False
            self.esctime = None
            while True:
                if (v := self._check_read_key()) is not None:
                    return v

                r = True
                d = b''
                rtime = None
                if endtime:
                    ctime = self.timefunc()
                    rtime = endtime - ctime
                    if rtime <= 0:
                        if allow_exit:
                            return None
                        rtime = 0

                if self.esctime:
                    rtime = self.esc_detect_time

                try:
                    r, _, _ = select.select([self.fd], [], [], rtime)
                except (EnvironmentError, select.error):
                    return None

                if r:
                    d = os.read(self.fd, 1)
                else:
                    allow_exit = True

                self.feed_bytes(d)

    class AsyncTTYInput(TTYInput):
        def __init__(self, fd=None, closefd=False, altscr=False, hidecurs=False,
                     altkeypad=False, signals=False, esc_detect_time=0.1, loop=None):
            if loop is None:
                loop = asyncio.get_running_loop()
            self.loop = loop
            self._waiter = None
            super().__init__(fd, closefd, altscr, hidecurs, altkeypad, signals, esc_detect_time, loop.time)
            loop.add_reader(self.fd, self._read_data)

        def close(self):
            self.loop.remove_reader(self.fd)
            super().close()

        def _wakeup(self):
            waiter = self._waiter
            if waiter is not None:
                self._waiter = None
                if not waiter.done():
                    waiter.set_result(None)

        def feed_bytes(self, data):
            super().feed_bytes(data)
            self._wakeup()

        def _read_data(self):
            try:
                data = os.read(self.fd, 16)
                self.feed_bytes(data)
            except IOError:
                pass

        async def readkey(self, endtime=None):
            self.esctime = None
            while True:
                if (v := self._check_read_key()) is not None:
                    return v

                ctime = self.timefunc()
                timeout_time = endtime
                timer = None

                if self.esctime:
                    timeout_time = self.esctime

                f = self._waiter = self.loop.create_future()
                if timeout_time is not None:
                    timer = self.loop.call_at(timeout_time, lambda: f.set_result(None))

                try:
                    await f
                finally:
                    if timer:
                        timer.cancel()
                    if self._waiter is f:
                        self._waiter = None
