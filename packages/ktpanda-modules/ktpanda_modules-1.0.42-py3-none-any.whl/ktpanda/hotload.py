# hotload.py
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
hotload
=======

A class which can reload its methods from a module when it detects changes.
'''

import sys
import traceback
from threading import Lock
from importlib import reload
from pathlib import Path

def _apply_methods(cls, module):
    modname = module.__name__
    removed_methods = set()
    for name, func in cls.__dict__.items():
        try:
            if func.__module__ == modname:
                removed_methods.add(name)
        except AttributeError:
            pass

    for name, func in module.__dict__.items():
        try:
            code = func.__code__
            if func.__module__ == modname and code.co_argcount >= 1 and code.co_varnames[0] == 'self':
                existing = getattr(cls, name, None)
                if existing is None or existing.__module__ == modname:
                    removed_methods.discard(name)
                    setattr(cls, name, func)
        except AttributeError as e:
            pass

    for name in removed_methods:
        delattr(cls, name)

class HotloadMeta(type):
    def __new__(cls, clsname, bases, typedict):
        newcls = super().__new__(cls, clsname, bases, typedict)
        if newcls.hotload_module is None:
            return newcls

        newcls._hotload_lock = Lock()
        path = newcls._hotload_path = Path(newcls.hotload_module.__file__)
        newcls._hotload_loadtime = path.stat().st_mtime
        _apply_methods(newcls, newcls.hotload_module)
        return newcls

class Hotload(metaclass=HotloadMeta):
    _hotload_lock = Lock()
    _hotload_loadtime = None
    _hotload_path = None
    hotload_module = None

    def report_reload(self, name, prev_mtime, new_mtime):
        print(f'Reloading {name} ({prev_mtime:.2f}, {new_mtime:.2f})...')

    def report_exception(self, method, exc_info):
        print(f'Exception calling {method}:', file=sys.stderr)
        traceback.print_exception(*exc_info)

    def on_hotload(self):
        self.try_call('init')

    def check_hotload(self, report_error=True):
        cls = type(self)
        with cls._hotload_lock:
            module = cls.hotload_module
            reloaded = False
            try:
                mtime = cls._hotload_path.stat().st_mtime
                if  mtime > cls._hotload_loadtime:
                    if report_error:
                        self.report_reload(module.__name__, cls._hotload_loadtime, mtime)

                    newmod = reload(module)
                    newmod.__loadtime = mtime

                    _apply_methods(cls, newmod)

                    cls.hotload_module = newmod
                    cls._hotload_loadtime = mtime
                    reloaded = True
            except Exception:
                if not report_error:
                    raise
                self.report_exception('check_hotload', sys.exc_info())

        if reloaded:
            self.on_hotload()

        return reloaded

    def try_call(self, f, *args, **kw):
        try:
            meth = getattr(self, f)
            return meth(*args, **kw)
        except Exception as e:
            self.report_exception(f, sys.exc_info())
            return None
