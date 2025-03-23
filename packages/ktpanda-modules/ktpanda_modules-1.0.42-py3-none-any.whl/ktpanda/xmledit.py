# xmledit.py
#
# Copyright (C) 2024 Katie Rust (katie@ktpanda.org)
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
xmledit
=======

Parses an XML document using Expat, and allows replacing nodes and text without affecting
the surrounding formatting.
'''

import re

from dataclasses import dataclass
from xml.parsers import expat
from weakref import ref
from io import BytesIO

def _xmlesc(pattern, esctbl, name):
    get = esctbl.get
    rxsub = re.compile(pattern).sub
    repl = lambda m: get(m.group(0))
    def xmlesc(text):
        return rxsub(repl, text)

    xmlesc.__name__ = name
    return xmlesc

_esctbl = {
    '&': '&amp;',
    '>': '&gt;',
    '<': '&lt;'
}

_esctbl_quot = dict(_esctbl)
_esctbl_quot['"'] = '&quot;'

_esctbl_squo = dict(_esctbl)
_esctbl_squo["'"] = '&squo;'

_chars_ws_nl = {9, 10, 13, 32}
_chars_ws = {9, 32}

xmlesc = _xmlesc(r'[&<>]', _esctbl, 'xmlesc')
xmlesc_quot = _xmlesc(r'[&<>\"]', _esctbl_quot, 'xmlesc_quot')
xmlesc_squo = _xmlesc(r'[&<>\']', _esctbl_squo, 'xmlesc_squo')

def _findspace_back(data, pos, chars):
    while pos > 0 and data[pos - 1] in chars:
        pos -= 1
    return pos

def _findspace_fwd(data, pos, chars):
    end = len(data)
    while pos < end and data[pos] in chars:
        pos += 1
    return pos

class Span:
    def __init__(self, data, pstart, pend):
        self._data = data
        self.start = pstart
        self.end = pend

    def copy(self):
        return Span(self._data, self.start, self.end)

    @property
    def data(self):
        return self._data[self.start : self.end]

    @property
    def xml(self):
        return self.data.decode('utf8')

    def leading_space(self, newlines=True):
        pos = _findspace_back(self._data, self.start, _chars_ws_nl if newlines else _chars_ws)
        return self._data[pos : self.start].decode('utf8')

    def trailing_space(self, newlines=True):
        pos = _findspace_fwd(self._data, self.end, _chars_ws_nl if newlines else _chars_ws)
        return self._data[self.start : pos].decode('utf8')

    def expand_leading(self, newlines=True):
        self.start = _findspace_back(self._data, self.start, _chars_ws_nl if newlines else _chars_ws)
        return self

    def trim_leading(self, newlines=True):
        self.start = _findspace_fwd(self._data, self.start, _chars_ws_nl if newlines else _chars_ws)
        return self

    def expand_trailing(self, newlines=True):
        self.end = _findspace_fwd(self._data, self.end, _chars_ws_nl if newlines else _chars_ws)
        return self

    def trim_trailing(self, newlines=True):
        self.end = _findspace_back(self._data, self.end, _chars_ws_nl if newlines else _chars_ws)
        return self

class Node:
    NullParent = None
    children = ()
    name = ''
    attrs = {}
    null = False

    def __init__(self, pos):
        self.outer_start = pos
        self.outer_end = None
        self._data = None

        self._weakparent = None
        self._weakprev = None
        self._weaknext = None

    def outer(self):
        return Span(self._data, self.outer_start, self.outer_end)

    def inner(self):
        return Span(self._data, self.inner_start, self.inner_end)

    def start_tag(self):
        return Span(self._data, self.outer_start, self.inner_end)

    def end_tag(self):
        return Span(self._data, self.inner_end, self.outer_end)

    def _innertext(self, lst):
        for c in self.children:
            c._innertext(lst)

    def innertext(self):
        lst = []
        self._innertext(lst)
        return ''.join(lst)

    def walk(self, func, level=0):
        func(self, level)

    def find(self, predicate):
        if predicate(self):
            return self

        for cn in self.children:
            if rv := cn.find(predicate):
                return rv
        return None

    def _findall(self, lst, predicate):
        if predicate(self):
            lst.append(self)

        for cn in self.children:
            cn._findall(lst, predicate)

    def findall(self, predicate):
        lst = []
        self._findall(lst, predicate)
        return lst

    @property
    def parent(self):
        wp = self._weakparent
        if wp is not None:
            wp = wp()

        return wp or Node.NullParent

    @property
    def next_sibling(self):
        wp = self._weaknext
        if wp is not None:
            return wp()
        return wp

    @property
    def prev_sibling(self):
        wp = self._weakprev
        if wp is not None:
            return wp()
        return wp

class Element(Node):
    def __init__(self, pos, name, attrs):
        super().__init__(pos)
        self.name = name
        self.inner_start = None
        self.inner_end = None
        self.attrs = attrs
        self.children = []

    def walk(self, func, level=0):
        func(self, level)
        for cn in self.children:
            cn.walk(func, level + 1)

class Text(Node):
    def __init__(self, pos, text):
        super().__init__(pos)
        self.text = text

    @property
    def inner_start(self):
        return self.outer_start

    @property
    def inner_end(self):
        return self.outer_end

    def _innertext(self, lst):
        lst.append(self.text)

    def innertext(self):
        return self.text

class _NullParent(Node):
    null = True

    def __bool__(self):
        return False

    @property
    def parent(self):
        return self

Node.NullParent = _NullParent(0)

class Parser:
    def __init__(self, data):
        if isinstance(data, str):
            data = data.encode('utf8')

        self._data = data

        self._prev_node = None
        self._prev_node_attr = None

        self._parser = None
        self._node_stack = None
        self._replacements = []
        self.root = None

        self._parse()

    def any_changes(self):
        return len(self._replacements) > 0

    def clear_changes(self):
        self._replacements.clear()

    def replace(self, span, data):
        if isinstance(data, str):
            data = data.encode('utf8')
        self._replacements.append((span.start, span.end, data))

    def insert(self, pos, data):
        if isinstance(data, str):
            data = data.encode('utf8')
        self._replacements.append((pos, pos, data))

    def replace_text(self, span, text):
        self.replace(span, xmlesc(text))

    def insert_text(self, pos, text):
        self.insert(pos, xmlesc(text))

    def toxml(self):
        return self.toxmlbytes().decode('utf8')

    def toxmlbytes(self):
        replacements = self._replacements
        replacements.sort()

        data = self._data
        last_end = 0

        out = []

        for (start, end, repl) in replacements:
            if start < last_end:
                start = last_end

            if end < start:
                end = start

            out.append(data[last_end : start])
            out.append(repl)

            last_end = end

        out.append(data[last_end:])
        return b''.join(out)

    def _parse(self):
        root = Element(0, 'root', {})
        self._node_stack = [root]
        p = self._parser = expat.ParserCreate('UTF-8')
        p.StartElementHandler = self._start_elem
        p.EndElementHandler = self._end_elem
        p.CharacterDataHandler = self._text
        p.DefaultHandlerExpand = self._default_handler
        try:
            p.Parse(self._data, True)
            end_pos = self._parser.CurrentByteIndex
            self._apply_end(end_pos)
            self.root = root

            if len(root.children) == 1:
                self.root = root.children[0]
            elif root.children:
                root.inner_start = root.outer_start = root.children[0].outer_start
                root.inner_end = root.outer_end = root.children[-1].outer_end

        finally:
            self._parser = None
            p.StartElementHandler = None
            p.EndElementHandler = None
            p.CharacterDataHandler = None
            p.DefaultHandlerExpand = None

    def _apply_end(self, pos):
        if self._prev_node_attr is not None:
            setattr(self._prev_node, self._prev_node_attr, pos)
            self._prev_node_attr = None

    def _add_node(self, node):
        top = self._node_stack[-1]
        if top.children:
            prev = top.children[-1]
            node._weakprev = ref(prev)
            prev._weaknext = ref(node)
        top.children.append(node)
        node._weakparent = ref(top)
        node._data = self._data

    def _default_handler(self, *d):
        self._apply_end(self._parser.CurrentByteIndex)

    def _start_elem(self, name, attrs):
        pos = self._parser.CurrentByteIndex
        self._apply_end(pos)

        node = Element(pos, name, attrs)

        self._add_node(node)
        self._node_stack.append(node)

        self._prev_node = node
        self._prev_node_attr = 'inner_start'

    def _end_elem(self, name):
        pos = self._parser.CurrentByteIndex
        self._apply_end(pos)

        if len(self._node_stack) > 1:
            node = self._node_stack.pop()
            node.inner_end = pos
            self._prev_node = node
            self._prev_node_attr = 'outer_end'

    def _text(self, data):
        pos = self._parser.CurrentByteIndex
        self._apply_end(pos)

        self._prev_node_attr = 'outer_end'
        top = self._node_stack[-1]
        if top.children:
            prev = top.children[-1]
            if isinstance(prev, Text) and prev.outer_end == pos:
                prev.text += data
                self._prev_node = prev
                return

        node = Text(pos, data)
        self._add_node(node)
        self._prev_node = node
