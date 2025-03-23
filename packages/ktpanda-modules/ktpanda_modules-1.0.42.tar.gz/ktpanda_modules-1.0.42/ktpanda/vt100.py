# vt100.py
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
vt100
=====

Constants for VT100/Xterm control sequences. Import as `from ktpanda import vt100 as vt` for convenience.
'''

def cseq(c, *t):
    return '\033[%s%s%s' %(c[1:], ';'.join(str(v) for v in t), c[0])

CR           = '\r'
RESET        = '\x1bc'
NEXTLINE     = '\x1b[0K\n'
CLEAR        = '\r\x1b[0K'
CLEARBELOW   = '\x1b[0J'
RETURNTOP    = '\x1b[f'
CURSUP       = '\x1b[A'

BLACK        = '\x1b[30m'
RED          = '\x1b[31m'
GREEN        = '\x1b[32m'
YELLOW       = '\x1b[33m'
BLUE         = '\x1b[34m'
MAGENTA      = '\x1b[35m'
CYAN         = '\x1b[36m'
WHITE        = '\x1b[37m'
DEFAULT      = '\x1b[39m'

BGBLACK      = '\x1b[40m'
BGRED        = '\x1b[41m'
BGGREEN      = '\x1b[42m'
BGYELLOW     = '\x1b[43m'
BGBLUE       = '\x1b[44m'
BGMAGENTA    = '\x1b[45m'
BGCYAN       = '\x1b[46m'
BGWHITE      = '\x1b[47m'
BGDEFAULT    = '\x1b[49m'

BRBLACK      = '\x1b[90m'
BRRED        = '\x1b[91m'
BRGREEN      = '\x1b[92m'
BRYELLOW     = '\x1b[93m'
BRBLUE       = '\x1b[94m'
BRMAGENTA    = '\x1b[95m'
BRCYAN       = '\x1b[96m'
BRWHITE      = '\x1b[97m'
BRDEFAULT    = '\x1b[99m'

BGBRBLACK    = '\x1b[100m'
BGBRRED      = '\x1b[101m'
BGBRGREEN    = '\x1b[102m'
BGBRYELLOW   = '\x1b[103m'
BGBRBLUE     = '\x1b[104m'
BGBRMAGENTA  = '\x1b[105m'
BGBRCYAN     = '\x1b[106m'
BGBRWHITE    = '\x1b[107m'
BGBRDEFAULT  = '\x1b[109m'

BOLD         = '\x1b[1m'
NOBOLD       = '\x1b[22m'

UNDERLINE    = '\x1b[4m'
NOUNDERLINE  = '\x1b[24m'

BLINK        = '\x1b[5m'
NOBLINK      = '\x1b[25m'

INVERSE      = '\x1b[7m'
NOINVERSE    = '\x1b[27m'

NORM         = '\x1b[22;39m'

WRAPON       = '\x1b[?7h'
WRAPOFF      = '\x1b[?7l'

CURSON       = '\x1b[?25h'
CURSOFF      = '\x1b[?25l'

DECNKMON     = '\x1b[?66h'
DECNKMOFF    = '\x1b[?66l'

DECBKMON     = '\x1b[?67h'
DECBKMOFF    = '\x1b[?67l'

MOUSEON      = '\x1b[?1000h'
MOUSEOFF     = '\x1b[?1000l'

MOUSEHILITEON = '\x1b[?1001h'
MOUSEHILITEOFF = '\x1b[?1001l'

MOUSECELLON  = '\x1b[?1002h'
MOUSECELLOFF = '\x1b[?1002l'

MOUSEALLON   = '\x1b[?1003h'
MOUSEALLOFF  = '\x1b[?1003l'

ALTNLON      = '\x1b[?1035h'
ALTNLOFF     = '\x1b[?1035l'

METAESCON    = '\x1b[?1036h'
METAESCOFF   = '\x1b[?1036l'

DELKEYPADON  = '\x1b[?1037h'
DELKEYPADOFF = '\x1b[?1037l'

ALTSCRON     = '\x1b[?1049h'
ALTSCROFF    = '\x1b[?1049l'

BKTPASTEON   = '\x1b[?2004h'
BKTPASTEOFF  = '\x1b[?2004l'

KPON         = '\x1b='
KPOFF        = '\x1b>'

# Keymap
# 1;2X = shift
# 1;3X = alt
# 1;4X = alt+shift
# 1;5X = ctrl
# 1;6X = ctrl+shift
# 1;7X = ctrl+alt
# 1;8X = ctrl+alt+shift

BASE_CODES = [
    ('1', 'A', 'up'),
    ('1', 'B', 'down'),
    ('1', 'C', 'right'),
    ('1', 'D', 'left'),
    ('1', 'F', 'end'),
    ('1', 'H', 'home'),
    ('1', 'P', 'f1'),
    ('1', 'Q', 'f2'),
    ('1', 'R', 'f3'),
    ('1', 'S', 'f4'),
    ('1', '~', 'home'),
    ('2', '~', 'ins'),
    ('3', '~', 'del'),
    ('4', '~', 'end'),
    ('5', '~', 'pgup'),
    ('6', '~', 'pgdn'),
    ('15', '~', 'f5'),
    ('17', '~', 'f6'),
    ('18', '~', 'f7'),
    ('19', '~', 'f8'),
    ('20', '~', 'f9'),
    ('21', '~', 'f10'),
    ('23', '~', 'f11'),
    ('24', '~', 'f12'),
]

KEYMAP = {
    '\r': 'enter',
    '\n': 'enter',
    '\t': 'tab',
    '\x1b': 'esc',
    '\x7f': 'backspace',
    '\x08': 'backspace',
}

def _init_keymap():
    for j in range(8):
        mods = ''
        if j & 4:
            mods += 'ctrl+'
        if j & 2:
            mods += 'alt+'
        if j & 1:
            mods += 'shift+'
        for pfx, sfx, key in BASE_CODES:
            KEYMAP[f'\x1b[{pfx};{j+1}{sfx}'] = mods + key

    for pfx, sfx, key in BASE_CODES:
        if pfx == '1':
            pfx = ''
            KEYMAP[f'\x1bO{sfx}'] = key

        KEYMAP[f'\x1b[{pfx}{sfx}'] = key
        KEYMAP[f'\x1b\x1b[{pfx}{sfx}'] = 'alt+' + key

_init_keymap()

if __name__ == '__main__':
    def mkconst(name, val):
        globals()[name] = val
        print(f"{name:12} = {val!r}")

    def csconst(name, c, *val):
        mkconst(name, cseq(c, *val))

    def _init_attrs():
        colors = [(name, val) for val, name in enumerate(('BLACK', 'RED', 'GREEN', 'YELLOW', 'BLUE', 'MAGENTA', 'CYAN', 'WHITE', None, 'DEFAULT')) if name]
        attrs = [(name, val) for val, name in enumerate((None, 'BOLD', None, None, 'UNDERLINE', 'BLINK', None, 'INVERSE')) if name]

        toggles = [
            ('WRAP', 7),             # Wrap to next line
            ('CURS', 25),            # Show cursor
            ('DECNKM', 66),          # Application Keypad
            ('DECBKM', 67),          # Backarrow key sends backspace
            ('MOUSE', 1000),         # Send Mouse X & Y on button press and release
            ('MOUSEHILITE', 1001),   # Use Hilite Mouse Tracking
            ('MOUSECELL', 1002),     # Use Cell Motion Mouse Tracking.
            ('MOUSEALL', 1003),      # Use All Motion Mouse Tracking.
            ('ALTNL', 1035),         # Enable special modifiers for Alt and NumLock keys.
            ('METAESC', 1036),       # Send ESC when Meta modifies a key (enables the metaSendsEscape resource).
            ('DELKEYPAD', 1037),     # Send DEL from the editing-keypad Delete key
            ('ALTSCR', 1049),        # Alternate screen mode
            ('BKTPASTE', 2004),      # Bracketed paste mode
        ]

        mkconst('CR', '\r')
        mkconst('RESET', '\033c')
        mkconst('NEXTLINE', cseq('K', 0) + '\n')
        mkconst('CLEAR', CR + cseq('K', 0))
        csconst('CLEARBELOW', 'J', 0)
        csconst('RETURNTOP', 'f')
        csconst('CURSUP', 'A')
        print()

        for pfx, base in [('', 30), ('BG', 40), ('BR', 90), ('BGBR', 100)]:
            for name, val in colors:
                csconst(pfx + name, 'm', base + val)
            print()

        for name, val in attrs:
            csconst(name, 'm', val)
            csconst('NO' + name, 'm', 20 + (2 if name == 'BOLD' else val))
            print()

        csconst('NORM', 'm', 22, 39)
        print()

        for name, code in toggles:
            csconst(name + 'ON', 'h?', code)
            csconst(name + 'OFF', 'l?', code)
            print()

        mkconst('KPON', '\033=')
        mkconst('KPOFF', '\033>')

    _init_attrs()
