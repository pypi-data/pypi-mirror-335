# sqlite_helper.py
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
sqlite_helper
=============

A wrapper class for an SQLite database that includes schema versioning and
various helper methods.
'''

import sys
import re
import sqlite3
import functools
import urllib.parse
from typing import Callable, Optional, Union, Any
from collections.abc import Iterable
from pathlib import Path

from .dictutils import JsonDict

def retry(func, *args):
    while True:
        try:
            return func(*args)
        except sqlite3.OperationalError as err:
            if str(err) != 'database is locked':
                raise

def in_transaction(func:Optional[Callable]=None, mode:str='DEFERRED', attr:Optional[str]=None) -> Callable:
    '''Decorator for methods which write to the database which wraps the function in a
    call to `retry_transaction`. `mode` is "DEFERRED" (default), "IMMEDIATE", or
    "EXCLUSIVE". If specified `attr` is the name of an attribute on the current object
    which references the SQLiteDB object (to support the delegate model).'''

    # Support @in_transaction(mode)
    #
    # If only one argument was passed positionally and it's a string, treat it as `mode`
    # instead of `func`.
    if isinstance(func, str):
        mode = func
        func = None

    if func is None:
        return functools.partial(in_transaction, mode=mode, attr=attr)

    def wrapper(self, *a, **kw):
        db = getattr(self, attr) if attr else self
        return db.retry_transaction(func, self, *a, mode=mode, **kw)
    functools.update_wrapper(wrapper, func)
    return wrapper

def split_schema(text:str) -> list:
    '''Split `text` into a list of individual SQL statements. Each statement should be
    terminated by a double-semicolon (;;). This allows for the definition of triggers
    which contain multiple statements.'''
    lst = [statement.strip() for statement in text.split(';;')]
    return [statement for statement in lst if statement]

def build_uri(path:Union[str, Path], *, readonly:bool=False, **kw):
    if readonly:
        kw['mode'] = 'ro'
        kw['immutable'] = 'true'

    uri = f'file:///' + urllib.parse.quote(str(Path(path).absolute()), safe=':\\/')
    if kw:
        uri += '?' + '&'.join(f'{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(val)}' for key, val in kw.items())
    return uri

class Cursor(sqlite3.Cursor):
    '''Subclass of sqlite3.Cursor which supports use as a context manager.'''
    _helper_db = None
    def execute(self, sql, parameters=()):
        if self._helper_db and self._helper_db.explain:
            self._helper_db._do_explain(sql, parameters)

        return super().execute(sql, parameters)

    def executemany(self, sql, parameters):
        if self._helper_db and self._helper_db.explain:
            self._helper_db._do_explain(sql, parameters)

        return super().executemany(sql, parameters)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self.close()

class SQLiteDB:
    PRAGMA_journal_mode = 'WAL'
    PRAGMA_synchronous = 'NORMAL'
    PRAGMA_page_size = 8192
    PRAGMA_recursive_triggers = True
    PRAGMA_legacy_file_format = False
    PRAGMA_foreign_keys = True

    check_same_thread = True
    timeout = 15.0

    common_schema = ['''
    CREATE TABLE IF NOT EXISTS vars (
      name TEXT PRIMARY KEY,
      value
    ) WITHOUT ROWID
    ''']

    schema_version = 1

    def __init__(self, path:Union[Path, str], *, readonly:bool=False):
        self.dbpath:Path = Path(path)
        self.readonly:bool = readonly
        self.explain:bool = False
        self.explained:set = set()
        self.backend = None
        self._in_transaction:bool = False

    def _open_db(self):
        return sqlite3.connect(
            build_uri(self.dbpath, readonly=self.readonly),
            check_same_thread=self.check_same_thread,
            timeout=self.timeout,
            uri=True
        )

    def connect(self, backend=None):
        if self.backend is not None:
            return

        if backend is None:
            backend = self._open_db()

        self.backend = backend
        for key in dir(self):
            if key.startswith('PRAGMA_'):
                text = value = getattr(self, key)
                if isinstance(value, bool):
                    text = 'ON' if value else 'OFF'
                sql = f'PRAGMA {key[7:]} = {text}'
                self.backend.execute(sql)

        self.exec_schema(self._get_common_commands())
        self._check_version()

    def exec_schema(self, schema:Iterable[str]):
        '''Executes an array of statements directly'''
        for cmd in schema:
            if not cmd.strip():
                continue

            try:
                with self.cursor() as curs:
                    curs.execute(cmd)
            except Exception:
                print(f'Error executing {cmd}', file=sys.stderr)
                raise

    def _check_version(self):
        cvers = self.backend.execute('PRAGMA user_version').fetchone()[0]
        if cvers < self.schema_version:
            self.backend.execute('BEGIN EXCLUSIVE')
            if cvers != 0:
                self._do_upgrade(cvers, self.schema_version, 'upgrade')

            self.exec_schema(self.common_schema)
            if cvers == 0:
                self._init_db()
            else:
                self._do_upgrade(cvers, self.schema_version, 'postupgrade')
            self.backend.execute(f'PRAGMA user_version = {self.schema_version}')
            self.commit()

    def _init_db(self):
        pass

    def _do_upgrade(self, oldvers, newvers, func):
        for v in range(oldvers + 1, newvers + 1):
            ugf = getattr(self, f'_{func}_to_{v}', None)
            if ugf:
                ugf(oldvers)

    def _get_common_commands(self):
        return []

    def alter_schema(self, *mods, check:bool=True, debug:bool=False):
        sqlite_schema_version = list(self.backend.execute('PRAGMA schema_version'))[0][0]

        self.backend.execute('PRAGMA writable_schema = ON')

        for mod in mods:
            if len(mod) == 6:
                select_criteria, args, prefix, old, new, suffix = mod
                replace = lambda text: text.replace(prefix + old + suffix, prefix + new + suffix)
            elif len(mod) == 4:
                select_criteria, args, pattern, repl = mod
                if isinstance(pattern, str):
                    pattern = re.compile(pattern)
                replace = lambda text: pattern.sub(repl, text)
            elif len(mod) == 3:
                select_criteria, args, replace = mod
            else:
                raise ValueError(f'Invalid modification: {mod!r}')

            curs = self.backend.execute(f"SELECT type, name, sql FROM sqlite_master WHERE {select_criteria}")
            for type, name, oldsql in curs:
                newsql = replace(oldsql)
                if newsql != oldsql:
                    if debug:
                        print('=' * 80)
                        print(f'{type} {name}, previous SQL:')
                        print(oldsql)
                        print('=' * 80)
                        print(f'{type} {name}, new SQL:')
                        print(newsql)
                        print('=' * 80)
                    self.backend.execute('UPDATE sqlite_master SET sql = ? WHERE type = ? AND name = ?', (newsql, type, name))

        self.backend.execute(f'PRAGMA schema_version = {sqlite_schema_version + 1}')
        self.backend.execute('PRAGMA writable_schema = OFF')
        if check:
            self.backend.execute('PRAGMA integrity_check')

    def commit(self):
        return self.backend.commit()

    def rollback(self):
        self.backend.execute('ROLLBACK')

    def _do_explain(self, q:str, args:Iterable):
        if q in self.explained:
            return
        self.explained.add(q)
        print()
        print('=== ' + q)
        for row in self.backend.execute('EXPLAIN QUERY PLAN ' + q, args):
            print(f'   {row!r}')
        print()

    def cursor(self):
        curs = self.backend.cursor(Cursor)
        curs._helper_db = self
        return curs

    def execute(self, sql:str, parameters:Iterable=()):
        curs = self.backend.cursor(Cursor)
        curs._helper_db = self
        curs.execute(sql, parameters)
        return curs

    def executemany(self, sql:str, parameters:Iterable):
        curs = self.backend.cursor(Cursor)
        curs._helper_db = self
        curs.executemany(sql, parameters)
        return curs

    def execute_nonquery(self, q:str, args:Iterable=()):
        '''Execute a statement that will update rows but not return them, like 'INSERT',
        'UPDATE', or 'DELETE'. Returns a tuple of (rowcount, last_insert_rowid).'''
        if self.readonly:
            return 0, None

        with self.execute(q, args) as curs:
            return curs.rowcount, curs.lastrowid

    def query_list(self, q:str, args:Iterable=()):
        '''Runs the given query in full and returns rows as a list.'''
        with self.execute(q, args) as curs:
            rows = list(curs)
        return rows

    def query_one(self, q:str, args:Iterable=(), default:Any=None):
        '''Returns a single row from the query. If the query returns no rows, returns `default`.'''
        with self.execute(q, args) as curs:
            row = curs.fetchone()
        if row is not None:
            return row
        return default

    def query_scalar(self, q:str, args:Iterable=(), default:Any=None):
        '''Returns a single column from a single row. If the query returns no rows, returns `default`.'''
        return self.query_one(q, args, (default,))[0]

    def close(self):
        if self.backend is not None:
            self.backend.close()
            self.backend = None

    def getvar(self, name:str, default:Any=None):
        row = self.query_scalar('SELECT value FROM vars WHERE name = ?', (name,)).fetchone()
        if row:
            return row[0]
        return default

    def setvar(self, name:str, val:Any):
        self.execute_nonquery('INSERT OR REPLACE INTO vars VALUES(?, ?)', (name, val))

    def retry_transaction(self, func:Callable, *a, mode:str='DEFERRED', **kw):
        '''Begin a transaction and run func(). If the database is locked, rolls back and
        runs func() again until it succeeds. If it fails with any other exception, the
        database is rolled back
        '''

        if self.readonly or self._in_transaction:
            return func(*a, **kw)

        committed = False
        while True:
            try:
                self.backend.execute(f'BEGIN {mode}')
                self._in_transaction = True
                rv = func(*a, **kw)
                self.commit()
                committed = True
                return rv
            except sqlite3.OperationalError as err:
                if str(err) != 'database is locked':
                    raise

                # If func() tried to change the database but a conflict occured, then next
                # time we run, grab the write lock immediately.
                if mode.upper() == 'DEFERRED':
                    mode = 'IMMEDIATE'
            finally:
                if not committed:
                    # Might be the case that a transaction is not active
                    try:
                        self.rollback()
                    except sqlite3.OperationalError:
                        pass
                self._in_transaction = False

class Query:
    '''Utility class for building an SQL query'''

    def __init__(self, base=None):
        if base is not None:
            self._keys = list(base._keys)
            self._columns = list(base._columns)
            self._from = list(base._from)
            self._where = list(base._where)
            self._order = list(base._order)
            self._subqueries = list(base._subqueries)
            self._limit = base._limit
            self._distinct = base._distinct
        else:
            self._keys = []
            self._columns = []
            self._from = []
            self._where = []
            self._order = []
            self._subqueries = []
            self._limit = None
            self._distinct = False
            self.sql = None

    def copy(self):
        return Query(self)

    def distinct(self, newval=True):
        self._distinct = newval
        return self

    def add(self, tbl, *columns):
        self._keys.extend(columns)
        self._columns.extend(f'{tbl}.{col}' for col in columns)
        return self

    def addas(self, tbl, column, name):
        self._keys.append(name)
        self._columns.append(f'{tbl}.{column}')
        return self

    def addsql(self, sql, name):
        self._keys.append(name)
        self._columns.append(f'({sql})')
        return self

    def addcols(self, query):
        self._keys.extend(query._keys)
        self._columns.extend(query._columns)
        return self

    def subq(self, name, select):
        self._subqueries.append(f'{name} AS ({select})')
        return self

    def from_(self, tbl, shortname):
        self._from.append(f'FROM {tbl} {shortname}')
        return self

    def join(self, tbl, shortname, on):
        self._from.append(f'LEFT JOIN {tbl} {shortname} ON {shortname}.{on}')
        return self

    def where(self, cond):
        self._where.append(cond)
        return self

    def order(self, col, desc=False):
        self._order.append(col + (' DESC' if desc else ''))
        return self

    def limit(self, limit):
        self._limit = limit
        return self

    def build(self):
        text = []
        if self._subqueries:
            text.append('WITH')
            text.append(','.join(self._subqueries))

        text.append('SELECT')
        if self._distinct:
            text.append('DISTINCT')

        text.append(','.join(self._columns))
        text.append(' '.join(self._from))
        if self._where:
            text.append('WHERE (')
            text.append(') AND ('.join(self._where))
            text.append(')')
        if self._order:
            text.append('ORDER BY')
            text.append(', '.join(self._order))

        if self._limit is not None:
            text.append('LIMIT')
            text.append(self._limit)

        self.sql = ' '.join(text)
        return self

    def from_row(self, row):
        return JsonDict(zip(self._keys, row))

    def _run(self, db, args, kwargs):
        return [self.from_row(row) for row in db.execute(self.sql, args or kwargs)]

    def run(self, db, *args, **kwargs):
        return self._run(db, args, kwargs)

    def run_scalar(self, db, *args, **kwargs):
        rows = self._run(db, args, kwargs)
        return rows[0] if rows else None
