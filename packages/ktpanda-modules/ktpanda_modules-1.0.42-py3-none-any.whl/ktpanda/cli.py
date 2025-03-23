# cli.py
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
cli
===

Defines decorators which make it easy to create dispatch-style CLI interfaces
'''
import argparse

__all__ = ['Command', 'Parser', 'arg']

class Command:
    def __init__(self, name, parserkw, func, parser):
        self.name = name
        self.func = func
        self.parserkw = parserkw

        self.parser = parser
        self.subparsers = None

    def get_subparsers(self):
        if self.subparsers is None:
            self.subparsers = self.parser.add_subparsers(
                title='Subcommands',
                help='Use %(prog)s <command> --help for subcommand usage',
                metavar='command'
            )
        return self.subparsers

class Parser:
    def __init__(self, *a, **kw):
        default_func = kw.pop('default_func', None)
        if default_func is None:
            default_func = lambda parser, args, *a, **kw: parser.print_help()
        self.root_parser = argparse.ArgumentParser(*a, **kw)
        self.root_parser.set_defaults(command_name=())

        self.commands = {
            (): Command((), {}, default_func, self.root_parser)
        }

    def command(self, *name, **parserkw):
        '''Decorator which defines a CLI command'''
        def rtn(func):
            parent_cmd = self.commands[name[:-1]]
            if 'description' not in parserkw:
                parserkw['description'] = parserkw.get('help')

            parser = parent_cmd.get_subparsers().add_parser(name[-1], **parserkw)
            parser.set_defaults(command_name=name)
            for argf in reversed(getattr(func, 'argfuncs', ())):
                argf(parser)

            self.commands[name] = Command(name, parserkw, func, parser)
            return func
        return rtn

    def get_command_for_args(self, args):
        return self.commands[args.command_name]

    def dispatch(self, args, *xargs):
        cmd = self.get_command_for_args(args)
        cmd.func(cmd.parser, args, *xargs)

def _arg(f, argf):
    try:
        args = f.argfuncs
    except AttributeError:
        args = f.argfuncs = []
    args.append(argf)
    return f

def arg(*a, **kw):
    completer = kw.pop('completer', None)
    def argf(p):
        arg = p.add_argument(*a, **kw)
        if completer:
            arg.completer = completer
    return lambda f: _arg(f, argf)
