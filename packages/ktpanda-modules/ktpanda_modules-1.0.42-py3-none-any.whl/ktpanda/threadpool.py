# threadpool.py
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
threadpool
==========

Maintains a pool of threads which can execute jobs.
'''

import sys
import traceback
import time
import threading

from collections import deque

__all__ = ["ThreadPool", "get_main_pool", "set_main_pool"]

DEBUG = False

class JobRunner(threading.Thread):
    def __init__(self, queue, job):
        threading.Thread.__init__(self, daemon=True)
        self.lock = threading.Lock()
        self.queue = queue
        self.job = job
        self.idletime = time.time()

    def run(self):
        wlock = self.lock
        queue = self.queue

        while True:
            wlock.acquire()
            if self.job is None:
                break

            f, a = self.job
            try:
                f(*a)
            except Exception:
                queue.report_exception(sys.exc_info())

            queue.finished(self)

        queue.thread_exit(self)

    def assign(self, job):
        self.job = job
        self.lock.release()

    def idle(self):
        self.job = None
        self.idletime = time.time()

class ThreadPool:
    def __init__(self, maxthreads = 10, minthreads = 0, maxbacklog = 50, timeout = None):
        self.minthreads = minthreads
        self.maxthreads = maxthreads
        self.maxbacklog = maxbacklog

        self.idle_timeout = timeout

        self.mutex = threading.Lock()

        self.can_put = threading.Condition(self.mutex)
        self.can_quit = threading.Condition(self.mutex)
        self.can_join = threading.Condition(self.mutex)

        # total jobs running and in queue
        self.total_jobs = 0

        # all running threads
        self.threads = set()

        # threads that are waiting for a job (idle)
        self.ithreads = deque()

        self.backlog = deque()
        self._id = 0

    def report_exception(self, exc_info):
        traceback.print_exception(*exc_info)

    def run(self, func, *args):
        job = func, args

        with self.mutex:
            self.total_jobs += 1

            if self.ithreads:
                thr = self.ithreads.pop()
                if DEBUG:
                    print("thread %3d: assigned job" % thr._id)

                thr.assign(job)
            elif len(self.threads) < self.maxthreads:
                thr = JobRunner(self, job)

                thr._id = self._id
                self._id += 1

                if DEBUG:
                    print("thread %3d: created" % thr._id)

                self.threads.add(thr)
                thr.start()
            else:
                if self.maxbacklog:
                    while len(self.backlog) >= self.maxbacklog:
                        self.can_put.wait()
                self.backlog.append(job)

    def quit(self):
        with self.mutex:
            self.backlog = None
            for thr in self.ithreads:
                thr.assign(None)
                if DEBUG:
                    print("thread %3d: cancelling" % thr._id)

            self.ithreads.clear()
            while self.threads:
                self.can_quit.wait()

    def join(self):
        with self.mutex:
            while self.total_jobs > 0:
                self.can_join.wait()


    def reap(self):
        if not self.idle_timeout:
            return
        mintime = time.time() - self.idle_timeout
        with self.mutex:
            if self.backlog is None:
                return
            maxreap = len(self.threads) - self.minthreads
            if maxreap <= 0:
                return
            ithreads = self.ithreads
            while ithreads:
                oldest = ithreads[0]
                if oldest.idletime >= mintime or maxreap == 0:
                    break
                ithreads.popleft()
                maxreap -= 1
                oldest.assign(None)
                if DEBUG:
                    print("thread %3d: reaped" % oldest._id)

    def finished(self, thr):
        with self.mutex:
            backlog = self.backlog
            if backlog is None:
                thr.assign(None)
                return

            if backlog:
                thr.assign(backlog.popleft())
                self.can_put.notify()
            else:
                thr.idle()
                self.ithreads.append(thr)
                if DEBUG:
                    print("thread %3d: idle" % thr._id)

            self.total_jobs -= 1
            if self.total_jobs == 0:
                self.can_join.notify_all()

    def thread_exit(self, thr):
        with self.mutex:
            self.threads.discard(thr)
            if DEBUG:
                print("thread %3d: exited" % thr._id)
            if not self.threads:
                self.can_quit.notify_all()

main_pool = None
def set_main_pool(pool):
    global main_pool
    main_pool = pool

def get_main_pool():
    return main_pool
