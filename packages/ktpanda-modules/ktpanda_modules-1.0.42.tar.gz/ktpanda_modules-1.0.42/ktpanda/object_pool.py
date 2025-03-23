# object_pool.py
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
object_pool
===========

Maintains a pool of objects which can be checked out as needed by different threads.
'''


import time
from collections import deque
from threading import Lock
from contextlib import contextmanager

_lock = Lock()
_pools = {}

DEBUG = False

class Pool:
    def __init__(self, clas, args):
        self.clas = clas
        self.args = args
        self.items = deque()

        self.items_out = 0

        self.lock = Lock()

    def __repr__(self):
        return "pool(%s%s) <%d, %d>" % \
            (self.clas.__name__, ''.join(', %r' % n for n in self.args),
             len(self.items), self.items_out)

    def _get(self):
        if DEBUG:
            print('%r: get object' % self)

        try:
            time, item = self.items.pop()
        except IndexError:
            item = self.clas(*self.args)

        self.items_out += 1
        return item

    def _put(self, item):
        self.items_out -= 1
        self.items.append((time.time(), item))
        if DEBUG:
            print('%r: put object' % self)

    def get(self):
        with self.lock:
            return self._get()

    @contextmanager
    def checkout(self):
        item = self.get()
        try:
            yield item
        finally:
            self.put(item)

    def put(self, item):
        with self.lock:
            self._put(item)


    def item_kept(self):
        with self.lock:
            self.items_out -= 1

    def clear(self):
        with self.lock:
            for i in self.items:
                i.close()
            self.items.clear()

    def reap(self, timeout):
        mintime = time.time() - timeout
        with self.lock:
            items = self.items
            numdel = 0
            while items:
                otime, item = items[0]
                if otime >= mintime:
                    break
                item.close()
                items.popleft()
                numdel += 1
            if DEBUG and numdel:
                print('%r: deleted %d objects' % (self, numdel))

            # If we have no more items, delete the pool.
            return self.items_out > 0 or len(self.items) > 0

def _getpool(clas, args):
    key = (id(clas), args)
    with _lock:
        try:
            return _pools[key]
        except KeyError:
            newpool = Pool(clas, args)
            _pools[key] = newpool
            return newpool


def getpool(clas, *args):
    return _getpool(clas, args)

def checkout(clas, *args):
    return _getpool(clas, args).checkout()

def reap_old_objects(timeout):
    if DEBUG:
        print('begin reaping (%d pools)' % len(_pools))

    with _lock:
        for key, p in list(_pools.items()):
            if not p.reap(timeout):
                del _pools[key]

    if DEBUG:
        print('end reaping (%d pools)' % len(_pools))
