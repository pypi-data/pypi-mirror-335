# git_filter.py
#
# PYTHON_ARGCOMPLETE_OK
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
git_filter
==========

A filter driver for Git which cam make local changes to a repository.
'''
import sys
import re
import time
import os
import argparse
import subprocess
import traceback
import struct
from io import BytesIO
from pathlib import Path

try:
    import argcomplete
except ImportError:
    argcomplete = None

RX_SPACE = re.compile(r'[ \t]*')

MAX_PACKET_CONTENT_SIZE = 65516
BOM = '\ufeff'
DEBUG = False

COMMENT_HASH = '# ', ''
COMMENT_C = '/* ', ' */'
COMMENT_XML = '<!-- ', ' -->'
COMMENT_CPP = '// ', ''
COMMENT_SEMI = '; ', ''
COMMENT_SQL = '-- ', ''

COMMENT_STYLE = {}

_COMMENT_EXT = [
    (COMMENT_HASH, 'py pl sh bash rb ex exs ps1 conf'),
    (COMMENT_C, 'c css'),
    (COMMENT_XML, 'html xml'),
    (COMMENT_CPP, 'c++ cpp java js swift php'),
    (COMMENT_SEMI, 'el scm asm ahk'),
    (COMMENT_SQL, 'sql lua ada'),
]

def get_comment_style(ext, path=None):
    if not COMMENT_STYLE:
        for style, extensions in _COMMENT_EXT:
            for extn in extensions.split():
                COMMENT_STYLE[extn] = style

    if ext == 'auto' and path:
        ext = path.suffix.strip('.')

    return COMMENT_STYLE.get(ext, COMMENT_HASH)

def line_begin(text, pos):
    try:
        return text.rindex('\n', 0, pos) + 1
    except ValueError:
        return 0

def line_end(text, pos):
    try:
        return text.index('\n', pos)
    except ValueError:
        return len(text)

def add_default_args(p):
    p.add_argument(
        '-s', '--smudge',
        dest='clean', action='store_false', default=None,
        help='Filter data from STDIN and apply working tree changes')

    p.add_argument(
        '-c', '--clean',
        dest='clean', action='store_true',
        help='Filter data from STDIN and undo working tree changes')

    p.add_argument(
        '-p', '--path', type=Path,
        help='Path to the file being processed')

    p.add_argument(
        '-P', '--process', action='store_true',
        help='Run the filter in "process" mode, filtering multiple files')

class GitFilter:
    debug = False

    def read_packet(self):
        length_data = sys.stdin.buffer.read(4)
        if not length_data:
            raise EOFError()

        if self.debug:
            print(f'length = {length_data!r}', file=sys.stderr)

        ln = int(length_data.decode('ascii'), 16)
        if ln == 0:
            pkt = None
        else:
            pkt = sys.stdin.buffer.read(ln - 4)

        if self.debug:
            print(f'read packet {ln} {pkt!r}', file=sys.stderr)

        return pkt

    def read_packet_text(self):
        data = self.read_packet()
        return None if data is None else data.decode('utf8').rstrip('\n')

    def write_packet(self, val):
        if isinstance(val, str):
            val = (val + '\n').encode('utf8')
        length_data = f'{len(val) + 4:04X}'.encode('ascii')
        if self.debug:
            print(f'write packet {length_data} {val!r}', file=sys.stderr)
        sys.stdout.buffer.write(length_data)
        sys.stdout.buffer.write(val)

    def flush(self):
        if self.debug:
            print('flush', file=sys.stderr)
        sys.stdout.buffer.write(b'0000')
        sys.stdout.buffer.flush()

    def expect_packet(self, expect):
        pkt = self.read_packet_text()
        if pkt != expect:
            raise ValueError(f'Expected {expect!r}, got {pkt!r}')

    def filter_bin(self, data, path, clean):
        return data

    def read_key_val(self):
        rtn = {}
        while True:
            pkt = self.read_packet_text()
            if pkt is None:
                return rtn
            key, _, val = pkt.partition('=')
            if key in rtn:
                rtn[key] = rtn[key] + '\n' + val
            else:
                rtn[key] = val

    def run_process(self):
        try:
            import msvcrt
            msvcrt.setmode (sys.stdin.fileno(), os.O_BINARY)
        except ImportError:
            pass

        ident = self.read_packet_text()
        if ident != 'git-filter-client':
            raise ValueError(f'Invalid ident {ident!r}')

        header = self.read_key_val()
        if header.get('version') != '2':
            raise ValueError(f'Invalid version {header.get("version")}')

        self.write_packet('git-filter-server')
        self.write_packet('version=2')
        self.flush()

        caps = self.read_key_val()

        self.write_packet('capability=clean')
        self.write_packet('capability=smudge')
        self.flush()

        while True:
            header = self.read_key_val()
            cmd = header['command']
            path = header['pathname']

            if not path:
                raise ValueError('Empty path')

            fp = BytesIO()
            while True:
                pkt = self.read_packet()
                if not pkt:
                    break
                fp.write(pkt)

            data = fp.getvalue()
            if cmd in {'clean', 'smudge'}:
                try:
                    newdata = self.filter_bin(data, Path(path), cmd == 'clean')
                except Exception:
                    traceback.print_exc()
                    self.write_packet('status=error')
                    self.flush()
                    continue
            else:
                raise ValueError('Invalid command: {command!r}')

            self.write_packet('status=success')
            self.flush()

            fp = BytesIO(newdata)
            while True:
                pkt = fp.read(MAX_PACKET_CONTENT_SIZE)
                if not pkt:
                    break
                self.write_packet(pkt)
            self.flush()
            self.flush()

    def filter_one(self, path, clean):
        data = sys.stdin.buffer.read()
        try:
            newdata = self.filter_bin(data, path, clean)
        except Exception:
            sys.stdout.buffer.write(data)
            traceback.print_exc()
        else:
            sys.stdout.buffer.write(newdata)

    def add_extra_arguments(self, p):
        pass

    def run_main_other(self):
        print('Must specify --smudge, --clean, or --process')

    def run_main(self, args=None):
        if os.getenv('GIT_FILTER_DEBUG'):
            GitFilter.debug = True

        if args is None:
            p = argparse.ArgumentParser(description='')
            add_default_args(p)
            self.add_extra_arguments(p)
            if argcomplete:
                argcomplete.autocomplete(p)

            args = p.parse_args()

        self.args = args
        if args.process:
            try:
                self.run_process()
            except EOFError:
                pass
        elif args.clean is not None:
            self.filter_one(args.path, args.clean)
        else:
            self.run_main_other()

class TextFilter(GitFilter):
    def clean_text(self, text, path, is_dos, has_bom, is_smudged):
        return text

    def smudge_text(self, text, path, is_dos, has_bom):
        return text

    def filter_bin(self, data, path, clean):
        isdos = False

        if data.startswith(b'\xff\xfe'):
            fmt = 'utf-16le'
        elif data.startswith(b'\xfe\xff'):
            fmt = 'utf-16be'
        else:
            fmt = 'utf8'

        try:
            text = data.decode(fmt)
        except UnicodeDecodeError:
            fmt = 'latin1'
            text = data.decode(fmt)

        has_bom = text.startswith(BOM)
        if has_bom:
            text = text[1:]

        isdos = '\r\n' in text
        if isdos:
            text = text.replace('\r\n', '\n')


        # Run the `clean` filter
        text = self.clean_text(text, path, isdos, has_bom, clean)
        if not clean:
            text = self.smudge_text(text, path, isdos, has_bom)

        if isdos:
            text = text.replace('\n', '\r\n')
        if has_bom:
            text = BOM + text

        return text.encode(fmt)

class MultiBinFilter(GitFilter):
    def __init__(self, filters):
        super().__init__()
        self.filters = filters

    def filter_bin(self, data, path, clean):
        order = reversed(self.filters) if clean else self.filters
        for cf in order:
            data = cf.filter_bin(data, path, clean)

class MultiTextFilter(TextFilter):
    def __init__(self, filters):
        super().__init__()
        self.filters = filters

    def clean_text(self, text, path, is_dos, has_bom, is_smudged):
        for cf in reversed(self.filters):
            text = cf.clean_text(text, path, is_dos, has_bom, is_smudged)
        return text

    def smudge_text(self, text, path, is_dos, has_bom):
        for cf in self.filters:
            text = cf.smudge_text(text, path, is_dos, has_bom)
        return text

class SimpleTextFilter(TextFilter):
    def __init__(self, search, replace, idempotent=True):
        self.search = search
        self.replace = replace
        self.idempotent = idempotent

    def clean_text(self, text, path, is_dos, has_bom, is_smudged):
        if is_smudged or self.idempotent:
            return text.replace(self.replace, self.search)

    def smudge_text(self, text, path, is_dos, has_bom):
        return text.replace(self.search, self.replace)

class InsertLineFilter(TextFilter):
    '''Inserts one or more lines of code after a matching line of code. `insert_after` is
    a regular expression, which should match some text in the file. `lines` will be
    inserted'''

    def __init__(self, insert_after, lines, marker_text='SMUDGE InsertLineFilter',
                 comment_style='auto', block=True):
        self.lines = lines
        self.comment_style = comment_style
        self.block = block
        self.marker_text = marker_text
        self.marker_esc = re.escape(marker_text)

        if isinstance(insert_after, str):
            insert_after = re.compile(insert_after)

        self.insert_after = insert_after

    def clean_text(self, text, path, is_dos, has_bom, is_smudged):
        comment_b, comment_e = map(re.escape, get_comment_style(self.comment_style, path))
        if self.block:
            remove_rx = (
                r'(?s)\n[\ \t]*'
                f'{comment_b}BEGIN {self.marker_esc}{comment_e}'
                r'.*?'
                f'{comment_b}END {self.marker_esc}{comment_e}'
                r'((?=\n)|$)')
        else:
            remove_rx = fr'(?s)\n[^\n]*{comment_b}LINE {self.marker_esc}{comment_e}((?=\n)|$)'
        return re.sub(remove_rx, '', text)

    def smudge_text(self, text, path, is_dos, has_bom):
        m = self.insert_after.search(text)
        if not m:
            return text

        comment_b, comment_e = get_comment_style(self.comment_style, path)

        # Find the end of the line where insert_after matched.
        insert_point = line_end(text, m.end())
        prev_line_begin = line_begin(text, m.start())

        pre_text = text[:insert_point]
        post_text = text[insert_point:]

        # Get the indentation of the first matching line
        indent = RX_SPACE.match(text, prev_line_begin).group(0)

        new_text = [pre_text]
        if self.block:
            new_text.append(f'\n{indent}{comment_b}BEGIN {self.marker_text}{comment_e}')
            for line in self.lines:
                new_text.append(f'\n{indent}{line}')
            new_text.append(f'\n{indent}{comment_b}END {self.marker_text}{comment_e}')
        else:
            for line in self.lines:
                new_text.append(f'\n{indent}{line} {comment_b}LINE {self.marker_text}{comment_e}')

        new_text.append(post_text)
        return ''.join(new_text)

class CommentOutFilter(TextFilter):
    def __init__(self, match, marker_text='SMUDGE CommentOutFilter', comment_style='auto', count=None):
        self.marker_text = marker_text
        self.marker_esc = re.escape(marker_text)
        self.count = count
        self.comment_style = comment_style

        if isinstance(match, str):
            match = re.compile(match, re.S)

        self.match = match

    def clean_text(self, text, path, is_dos, has_bom, is_smudged):
        comment_b, comment_e = map(re.escape, get_comment_style(self.comment_style, path))
        return re.sub(fr'(?s){comment_b}{self.marker_esc} \[([^\n]*)\]{comment_e}', r'\1', text)

    def smudge_text(self, text, path, is_dos, has_bom):
        comment_b, comment_e = get_comment_style(self.comment_style, path)

        comment_begin = f'{comment_b}{self.marker_text} ['
        comment_end = f']{comment_e}'
        out_text = []
        remaining_text = text
        count = self.count
        while True:
            if count is not None:
                if count == 0:
                    break
                count -= 1

            m = self.match.search(remaining_text)
            if not m:
                break

            split_a = line_begin(remaining_text, m.start())
            split_b = line_end(remaining_text, m.end())
            out_text.append(remaining_text[:split_a])
            comment_lines = remaining_text[split_a : split_b]
            remaining_text = remaining_text[split_b:]

            indent = RX_SPACE.match(comment_lines).group(0)
            for line in comment_lines.split('\n'):
                split_pos = len(indent) if line.startswith(indent) else 0
                out_text.append(
                    f'{line[:split_pos]}{comment_begin}{line[split_pos:]}{comment_end}'
                )
                out_text.append('\n')
            out_text.pop()

        out_text.append(remaining_text)
        return ''.join(out_text)

class AddSimpleFilterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        namespace.filters.append(SimpleTextFilter(*values))

class AddInsertFilterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        lines = values[1:]
        block = namespace.block if namespace.block is not None else len(lines) > 1
        namespace.filters.append(InsertLineFilter(values[0], lines, block=block))

class AddCommentFilterAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        count = None if len(values) < 2 else int(values[1])
        namespace.filters.append(CommentOutFilter(values[0], count=count))

def add_arguments_for_main(p):
    p.set_defaults(filters=[])

    add_default_args(p)

    p.add_argument(
        '-C', '--comment-style', default='auto',
        help='')

    p.add_argument(
        '--block', action='store_true',
        help='Use block mode for --insert (default: only if more than one line is inserted)')

    p.add_argument(
        '--no-block', dest='block', action='store_false',
        help='Never use block mode')

    p.add_argument(
        '--simple',
        dest='filters', action=AddSimpleFilterAction,
        nargs=2, metavar=('SEARCH', 'REPLACE'),
        help='')

    p.add_argument(
        '--insert',
        dest='filters', action=AddInsertFilterAction,
        nargs='+', metavar=('MATCH', 'LINES'),
        help='')

    p.add_argument(
        '--comment',
        dest='filters', action=AddCommentFilterAction,
        nargs='+', metavar=('MATCH', 'COUNT'),
        help='')

def run_main():
    p = argparse.ArgumentParser(prog='python -m ktpanda.git_filter', description='')
    add_arguments_for_main(p)

    if argcomplete:
        argcomplete.autocomplete(p)

    args = p.parse_args()

    if len(args.filters) == 0:
        p.print_help()
        return
    elif len(args.filters) == 1:
        filter = args.filters[0]
    else:
        filter = MultiTextFilter(args.filters)

    filter.run_main(args)

if __name__ == '__main__':
    run_main()
