# roundtrip_encoding.py
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
roundtrip_encoding
==================

Contains functions for converting between text and binary data in a way that unmodified
text data will be converted to the same binary data.
'''

import re

from collections import namedtuple

BOM = '\ufeff'

RoundTripEncoding = namedtuple('RoundTripEncoding', [
    'encoding', 'errors', 'has_bom', 'line_endings'])
RoundTripEncoding.__doc__ = r'''
Represents parameters for a round-trip encoding.

`encoding` and `errors` are the values passed to `str.encode()` and `bytes.decode()`. For
auto-detected encodings, `encoding` will be one of 'utf-8', 'utf-8-sig', 'utf-16le', or
'utf-16be', and `errors` will be `strict` or `surrogateescape`.

`has_bom` indicates that a byte-order mark (U+FEFF) was removed from the text *after*
decoding. Note that if `encoding` is 'utf-8-sig', then this will be False because the
codec itself removes the BOM.

`line_endings` indicates what line endings were in use in the original file:
* 'unix': The file contained *only* UNIX line endings ('\n').
* 'dos': The file contained *only* DOS line endings ('\r\n') and these have been converted
  to '\n'.
* 'mixed': The file contained a mix of DOS and UNIX line endings, and these have been left
  verbatim in the decoded text.
* 'none': The file contained no line endings.
* 'raw': Line ending conversion was disabled.
'''

def roundtrip_decode(data: bytes, remove_bom:bool=True, convert_line_endings:bool=True,
                     fallback_encoding:str=None, encoding:str=None,
                     errors:str='strict') -> (str, RoundTripEncoding):

    '''Convert a binary file into text in a way that can be converted back with the same
    encoding.

    If the file begins with the bytes FF FE, then it is decoded as UTF-16LE. If it starts
    with FE FF, it is decoded as UTF-16BE. Otherwise, the file is assumed to be UTF-8.

    `fallback_encoding`, if set, should be a single-byte encoding that maps every possible
    byte to a unique Unicode codepoint (such as 'iso-8859-1'), otherwise round-trip
    encoding cannot be guaranteed.

    If decoding fails, and `fallback_encoding` is not set, then the file will be decoded
    as UTF-8 with the 'surrogateescape' error handler

    `encoding` and `errors` can be set to force a specific encoding, but round-trip
    encoding cannot be guaranteed in that case.

    If `remove_bom` is True (default), then if the file starts with a byte-order mark
    (U+FEFF), it will be removed from the resulting text and noted in the returned
    RoundTripEncoding.

    If `convert_line_endings` is True (default), and the file contains *only* DOS line
    endings ('\r\n'), then all line endings will be converted to '\n' and noted in the
    returned encoding. If `convert_line_endings` is False, `line_endings` will be set to
    'raw'.

    The following is guaranteed to be true for all byte streams when `encoding`, `errors`,
    and `fallback_encoding` are left at default values:

    >>> text, encoding = roundtrip_decode(input_data)
    >>> assert input_data == roundtrip_encode(text, encoding)
    '''
    if encoding is None:
        if data.startswith(b'\xef\xbb\xbf') and remove_bom:
            encoding = 'utf-8-sig'
        elif data.startswith(b'\xff\xfe'):
            encoding = 'utf-16le'
        elif data.startswith(b'\xfe\xff'):
            encoding = 'utf-16be'
        else:
            encoding = 'utf8'

    try:
        text = data.decode(encoding, errors)
    except UnicodeDecodeError:
        if fallback_encoding is None:
            encoding = 'utf8'
            errors = 'surrogateescape'
        else:
            encoding = fallback_encoding
        text = data.decode(encoding, errors)


    if remove_bom:
        has_bom = text.startswith(BOM) and encoding != 'utf-8-sig'
        if has_bom:
            text = text[1:]
    else:
        has_bom = False

    if convert_line_endings:
        line_ending_set = set(re.findall(r'\r?\n', text))
        if line_ending_set == {'\r\n'}:
            line_endings = 'dos'
            text = text.replace('\r\n', '\n')
        elif line_ending_set == {'\n'}:
            line_endings = 'unix'
        elif len(line_ending_set) == 0:
            line_endings = 'none'
        else:
            line_endings = 'mixed'
    else:
        line_endings = 'raw'

    return text, RoundTripEncoding(encoding, errors, has_bom, line_endings)

def roundtrip_encode(text: str, encoding: RoundTripEncoding) -> bytes:
    '''Encode `text` using the parameters of `encoding`. First, if `encoding.line_endings`
    is 'dos', then all instances of '\n' are replaced with '\r\n', Then, if
    `encoding.has_bom` is `True`, then a byte-order mark is prepended to the text.
    Finally, the text is encoded using `encoding.encoding` and `encoding.errors` and the
    resulting `bytes` object is returned.'''

    encoding, errors, has_bom, line_endings = encoding

    if line_endings == 'dos':
        text = text.replace('\n', '\r\n')

    if has_bom:
        text = BOM + text

    return text.encode(encoding, errors)



class TextContent:
    '''Manages the contents of a file, converting between text and binary as necessary.'''

    def __init__(self, data):
        self.text_data = None
        self.bin_data = data
        self.roundtrip_encoding = RoundTripEncoding('utf8', 'strict', False, 'raw')
        self.changed = False
        #self._force_encoding
        self.inconsistent_line_endings = False

    @property
    def encoding(self):
        return self.roundtrip_encoding.encoding

    @property
    def has_bom(self):
        return self.roundtrip_encoding.has_bom or self.roundtrip_encoding.encoding == 'utf-8-sig'

    @property
    def line_endings(self):
        return self.roundtrip_encoding.line_endings

    def set_from(self, o):
        self.text_data = o.text_data
        self.bin_data = o.bin_data
        self.roundtrip_encoding = o.roundtrip_encoding

    def copy(self):
        new = type(self)(None)
        new.set_from(self)
        return new

    def __eq__(self, o):
        if not isinstance(o, TextContent):
            return False
        if self.text_data is not None and o.text_data is not None:
            return (self.text_data == o.text_data
                    and self.roundtrip_encoding == o.roundtrip_encoding)

        return self.get_binary() == o.get_binary()

    def get_text(self):
        '''Retrieves the current text, converting it from binary if necessary'''
        if self.text_data is not None:
            return self.text_data

        text, encoding = roundtrip_decode(self.bin_data)

        self.text_data = text
        self.roundtrip_encoding = encoding

        return text

    def get_binary(self):
        '''Retrieves the current binary data, converting it from text if necessary.'''
        if self.bin_data is not None:
            return self.bin_data

        data = roundtrip_encode(self.text_data, self.roundtrip_encoding)

        self.bin_data = data

        return data

    def set_text(self, text):
        '''Set the text content and clear cached binary content.'''
        if text != self.text_data:
            self.text_data = text
            self.bin_data = None
            self.changed = True
            return True
        return False

    def set_binary(self, data):
        '''Set the binary content and clear cached text content.'''
        if data != self.bin_data:
            self.bin_data = data
            self.text_data = None
            self.changed = True
            return True
        return False
