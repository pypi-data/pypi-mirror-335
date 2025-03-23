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
textcolor
=========

Utilities for dealing with VT100/Xterm 256 color text (at a higher level than the vt100 module)
'''

from unicodedata import category, east_asian_width

from ktpanda import vt100 as vt

BOLD = 0x100

CONSOLE_COLORS = [
    '000000', 'b21818', '18b218', 'b26818', '1818b2', 'b218b2', '18b2b2', 'b2b2b2',
    '686868', 'ff5454', '54ff54', 'ffff54', '5454ff', 'ff54ff', '54ffff', 'ffffff',
    '000000', '00005f', '000087', '0000af', '0000d7', '0000ff', '005f00', '005f5f',
    '005f87', '005faf', '005fd7', '005fff', '008700', '00875f', '008787', '0087af',
    '0087d7', '0087ff', '00af00', '00af5f', '00af87', '00afaf', '00afd7', '00afff',
    '00d700', '00d75f', '00d787', '00d7af', '00d7d7', '00d7ff', '00ff00', '00ff5f',
    '00ff87', '00ffaf', '00ffd7', '00ffff', '5f0000', '5f005f', '5f0087', '5f00af',
    '5f00d7', '5f00ff', '5f5f00', '5f5f5f', '5f5f87', '5f5faf', '5f5fd7', '5f5fff',
    '5f8700', '5f875f', '5f8787', '5f87af', '5f87d7', '5f87ff', '5faf00', '5faf5f',
    '5faf87', '5fafaf', '5fafd7', '5fafff', '5fd700', '5fd75f', '5fd787', '5fd7af',
    '5fd7d7', '5fd7ff', '5fff00', '5fff5f', '5fff87', '5fffaf', '5fffd7', '5fffff',
    '870000', '87005f', '870087', '8700af', '8700d7', '8700ff', '875f00', '875f5f',
    '875f87', '875faf', '875fd7', '875fff', '878700', '87875f', '878787', '8787af',
    '8787d7', '8787ff', '87af00', '87af5f', '87af87', '87afaf', '87afd7', '87afff',
    '87d700', '87d75f', '87d787', '87d7af', '87d7d7', '87d7ff', '87ff00', '87ff5f',
    '87ff87', '87ffaf', '87ffd7', '87ffff', 'af0000', 'af005f', 'af0087', 'af00af',
    'af00d7', 'af00ff', 'af5f00', 'af5f5f', 'af5f87', 'af5faf', 'af5fd7', 'af5fff',
    'af8700', 'af875f', 'af8787', 'af87af', 'af87d7', 'af87ff', 'afaf00', 'afaf5f',
    'afaf87', 'afafaf', 'afafd7', 'afafff', 'afd700', 'afd75f', 'afd787', 'afd7af',
    'afd7d7', 'afd7ff', 'afff00', 'afff5f', 'afff87', 'afffaf', 'afffd7', 'afffff',
    'd70000', 'd7005f', 'd70087', 'd700af', 'd700d7', 'd700ff', 'd75f00', 'd75f5f',
    'd75f87', 'd75faf', 'd75fd7', 'd75fff', 'd78700', 'd7875f', 'd78787', 'd787af',
    'd787d7', 'd787ff', 'd7af00', 'd7af5f', 'd7af87', 'd7afaf', 'd7afd7', 'd7afff',
    'd7d700', 'd7d75f', 'd7d787', 'd7d7af', 'd7d7d7', 'd7d7ff', 'd7ff00', 'd7ff5f',
    'd7ff87', 'd7ffaf', 'd7ffd7', 'd7ffff', 'ff0000', 'ff005f', 'ff0087', 'ff00af',
    'ff00d7', 'ff00ff', 'ff5f00', 'ff5f5f', 'ff5f87', 'ff5faf', 'ff5fd7', 'ff5fff',
    'ff8700', 'ff875f', 'ff8787', 'ff87af', 'ff87d7', 'ff87ff', 'ffaf00', 'ffaf5f',
    'ffaf87', 'ffafaf', 'ffafd7', 'ffafff', 'ffd700', 'ffd75f', 'ffd787', 'ffd7af',
    'ffd7d7', 'ffd7ff', 'ffff00', 'ffff5f', 'ffff87', 'ffffaf', 'ffffd7', 'ffffff',
    '080808', '121212', '1c1c1c', '262626', '303030', '3a3a3a', '444444', '4e4e4e',
    '585858', '626262', '6c6c6c', '767676', '808080', '8a8a8a', '949494', '9e9e9e',
    'a8a8a8', 'b2b2b2', 'bcbcbc', 'c6c6c6', 'd0d0d0', 'dadada', 'e4e4e4', 'eeeeee'
]

MISSING = object()

class Colorizer:
    def __init__(self, text=(), fg=None, bg=None):
        self.stack = []
        self.text = list(text)
        self.fg = fg
        self.bg = bg

    def _extend(self, seq, dfg, dbg):
        for text, (fg, bg) in seq:
            self.text.append((text, (fg or dfg, bg or dbg)))

    def set(self, fg=MISSING, bg=MISSING):
        if fg is not MISSING:
            self.fg = fg

        if bg is not MISSING:
            self.bg = bg

        return self

    def push(self, *a, **kw):
        self.stack.append((self.fg, self.bg))
        return self.set(*a, **kw)

    def pop(self):
        self.fg, self.bg = self.stack.pop()
        return self

    def t(self, arg, fg=MISSING, bg=MISSING, lpad=0, rpad=0, padchar=' '):
        if fg is MISSING:
            fg = self.fg

        if bg is MISSING:
            bg = self.bg

        if lpad or rpad:
            ln = txtattr_length(arg) if isinstance(arg, list) else len(arg)
            if lpad:
                rpad = 0
                if ln < lpad:
                    self.text.append((padchar * (lpad - ln), (self.fg, self.bg)))

        if isinstance(arg, Colorizer):
            self._extend(arg.text, self.fg, bg or self.bg)
        elif isinstance(arg, list):
            self._extend(arg, fg or self.fg, bg or self.bg)
            ln = txtattr_length(arg)
        else:
            self.text.append((arg, (fg or self.fg, bg or self.bg)))

        if rpad and ln < rpad:
            self.text.append((padchar * (rpad - ln), (self.fg, self.bg)))

        return self

    def copy(self):
        return type(self)(self.text, self.fg, self.bg)

    def _with_textlist(self, text):
        new = type(self)()
        new.text = list(text) if text is self.text else text
        new.fg = self.fg
        new.bg = self.bg
        return new

    def split(self, posa, posb=None):
        ta, tb = txtattr_split(self.text, posa)
        if posb is not None:
            tb, tc = txtattr_split(tb, posb)
            return self._with_textlist(ta), self._with_textlist(tb), self._with_textlist(tc)
        else:
            return self._with_textlist(ta), self._with_textlist(tb)


    def highlight(self, regex, attr):
        return self._with_textlist(txtattr_highlight(self.text, regex, attr))

    def highlight_inplace(self, regex, attr):
        self.text = txtattr_highlight(self.text, regex, attr)

    def replace_nprint(self):
        return self._with_textlist(replace_nprint(self.text))

    def replace_nprint_inplace(self):
        self.text = replace_nprint(self.text)

    def expand(self):
        return txtattr_expand(self.text)

    def collapse(self):
        return self._with_textlist(txtattr_collapse(self.text))

    def collapse_inplace(self):
        self.text = txtattr_collapse(self.text)

    def __getitem__(self, item):
        if not isinstance(item, slice):
            item = slice(item, item + 1)

        if item.step not in {None, 1}:
            raise ValueError(f'`step` not supported for {type(self).__name__}')

        ln = txtattr_length(self.text)

        start = item.start
        stop = item.stop
        if stop is not None and stop < 0:
            stop += ln

        if start is not None and start < 0:
            start += ln

        text = self.text
        if start:
            text = txtattr_split(text, start)[1]

        if stop is not None and stop < ln:
            text = txtattr_split(text, stop)[0]

        return self._with_textlist(text)

    def __iadd__(self, t):
        self.t(t)
        return self

    def __add__(self, o):
        return self.copy().t(o)

    def get(self, maxw=1000):
        return make_text_attr(self.text, maxw)

    def getplain(self):
        return txtattr_text(self.text)

    def __len__(self):
        return txtattr_length(self.text)

    def __str__(self):
        return self.getplain()

    def __repr__(self):
        return f'Colorizer({self.text!r})'

color_cache = {}

def decode_hcolor(hc):
    if len(hc) < 6:
        return [int(h+h, 16) for h in hc[:3]]
    return [int(hc[i:i+2], 16) for i in range(0, 6, 2)]

CONSOLE_COLOR_SEARCH = [(decode_hcolor(v), i) for i, v in enumerate(CONSOLE_COLORS)]

def clr_dist_sq(ca, cb):
    ra, ga, ba = ca
    rb, gb, bb = cb
    return (ra - rb) ** 2 + (ga - gb) ** 2 + (ba - bb) ** 2

def closest_color(hc):
    try:
        return color_cache[hc]
    except KeyError:
        pass
    if hc.startswith('!'):
        rv = BOLD | closest_color(hc[1:])
    else:
        ca = decode_hcolor(hc)
        rv = min(CONSOLE_COLOR_SEARCH, key=lambda v: clr_dist_sq(ca, v[0]))[1]
        if rv == 0:
            rv = 0x10

    color_cache[hc] = rv
    return rv

def split_cc(txt):
    for i, c in enumerate(txt):
        if category(c)[0] == 'C' or east_asian_width(c) in 'FW':
            return txt[:i], c, txt[i + 1:]
    return txt, '', ''

def replace_nprint(txt):
    rt = []
    for cstr, attr in txt:
        while cstr:
            pre, cc, cstr = split_cc(cstr)
            if pre:
                rt.append((pre, attr))
            if cc:
                fg, bg = attr
                if fg is None:
                    fg = 15
                if bg is None:
                    bg = 0
                invattr = bg, fg
                cpt = ord(cc)
                if cpt < 32:
                    rt.append(('^' + chr(cpt + 64), invattr))
                else:
                    rt.append(('<%02X>' % cpt, invattr))
    return rt

def nprint_length(txt):
    length = 0
    for ch in txt:
        if category(ch)[0] == 'C' or east_asian_width(ch) in 'FW':
            cpt = ord(ch)
            if cpt < 32:
                length += 2
            elif cpt < 0x100:
                length += 4
            elif cpt < 0x1000:
                length += 5
            elif cpt < 0x10000:
                length += 6
            elif cpt < 0x100000:
                length += 7
            else:
                length += 8
        else:
            length += 1
    return length

def txtattr_length(txtlist):
    return sum(len(txt) for txt, attr in txtlist)

def txtattr_text(txtlist):
    return ''.join(txt for txt, attr in txtlist)

def txtattr_expand(txtlist):
    rt = []
    for cstr, attr in txtlist:
        for ch in cstr:
            rt.append((ch, attr))
    return rt

def txtattr_collapse(txtlist):
    lattr = None
    rt = []
    ctxt = []
    for cstr, attr in txtlist:
        if not cstr:
            continue
        if lattr != attr:
            if ctxt:
                rt.append((''.join(ctxt), lattr))
            ctxt = []
        ctxt.append(cstr)
        lattr = attr

    if ctxt and lattr:
        rt.append((''.join(ctxt), lattr))
    return rt

def txtattr_split(txtlist, pos):
    rta = []
    rtb = []
    itr = iter(txtlist)
    for cstr, attr in itr:
        if pos < len(cstr):
            if pos > 0:
                rta.append((cstr[:pos], attr))
            rtb.append((cstr[pos:], attr))
            rtb.extend(itr)
            return rta, rtb
        rta.append((cstr, attr))
        pos -= len(cstr)
    return rta, rtb

def txtattr_highlight(txtlist, regex, attr):
    matches = list(regex.finditer(txtattr_text(txtlist)))
    if not matches:
        return txtlist

    ntxt = []
    lpos = 0
    for m in matches:
        b, e = m.span()
        prev, sm = txtattr_split(txtlist, b - lpos)
        sm, txtlist = txtattr_split(sm, e - b)
        lpos = e
        ntxt.extend(prev)
        newattr = (attr if isinstance(attr, tuple) else attr(m))
        ntxt.append((txtattr_text(sm), newattr))
    ntxt.extend(txtlist)
    return ntxt

def color_fg(c):
    if c is None:
        return vt.NORM

    if isinstance(c, str):
        c = closest_color(c)

    clr = f'\033[38;5;{c & 0xFF}m'
    if c & BOLD:
        return clr + vt.BOLD
    return clr

def color_bg(c):
    if c is None:
        return vt.BGDEFAULT

    if isinstance(c, str):
        c = closest_color(c)

    return f'\033[48;5;{c & 0xFF}m'

def make_text_attr(txtlist, maxw, skip=0, eraserest=True, restore=True):
    lfg = None
    lbg = None
    ret = []
    remain = maxw
    for txt, (fg, bg) in txtlist:
        if skip > 0:
            nskip = skip - len(txt)
            txt = txt[skip:]
            skip = nskip
        if not remain:
            break
        txt = txt[:remain]
        if not txt:
            continue
        remain -= len(txt)

        if fg != lfg:
            ret.append(color_fg(fg))
            lfg = fg

        if bg != lbg:
            ret.append(color_bg(bg))
            lbg = bg

        ret.append(txt)

    if restore:
        if lfg is not None:
            ret.append(color_fg(None))
        if lbg is not None:
            ret.append(color_bg(None))
    if eraserest and remain:
        ret.append('\033[K')
    return ''.join(ret)
