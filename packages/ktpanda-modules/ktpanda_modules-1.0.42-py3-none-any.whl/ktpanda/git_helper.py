'''
git_helper
==========

Contains a class, `Git`, for working with a Git repository
'''

import sys
import os
import re
import subprocess
from urllib.parse import urlparse, urlunparse
from pathlib import Path
from contextlib import contextmanager

def _quote_arg(arg):
    '''Quote an argument for debug output. Not intended as a general-purpose shell
    quoting function.'''
    if re.match(r'^[a-z0-9\-]+$', str(arg), re.I):
        return arg
    return f'"{arg}"'

class Git:
    def __init__(self, repo_path='.', git_exe=None, verbose=False, token=None):
        self.repo_path = Path(repo_path)
        self.verbose = verbose
        self.token = token
        if git_exe is None:
            git_exe = os.environ.get('GIT', 'git')
        self.git_exe = git_exe
        self.env_vars = {}

    def add_token(self, url):
        '''Adds `self.token` as a password to the given URL if a username is present.'''
        parsed_url = urlparse(url)
        if self.token and parsed_url.password is None and parsed_url.username is not None:
            new_netloc = f'{parsed_url.username}:{self.token}@{parsed_url.hostname}'
            if parsed_url.port is not None:
                new_netloc += f':{parsed_url.port}'
            return urlunparse(parsed_url._replace(netloc=new_netloc))
        return url

    @contextmanager
    def temp_remote(self, url):
        '''
        Context manager to temporarily add a remote to the configuration file. Note that
        any repository configuration changes made within the block may be reverted
        afterward.

        If `url' is a plain name, then it is returned verbatim and nothing is added to
        the config file.
        '''

        if not ':' in url:
            yield url
            return

        remote_name = 'temp-remote-' + os.urandom(6).hex()
        config_path = self.repo_path / '.git' / 'config'
        if not config_path.exists():
            config_path = Path(self.run_capt(['rev-parse', '--git-path', 'config']))

        url = self.add_token(url)

        current_text = config_path.read_text(encoding='utf8')
        new_text = (
            current_text + '\n'
            f'[remote "{remote_name}"]\n'
            f'\turl = {url}\n'
            f'\tfetch = +refs/heads/*:refs/remotes/{remote_name}/*\n'
        )

        try:
            config_path.write_text(new_text, encoding='utf8')
            yield remote_name
        finally:
            config_path.write_text(current_text, encoding='utf8')

    def _get_env(self):
        if self.env_vars:
            retv = dict(os.environ)
            retv.update(self.env_vars)
            return retv

        return None

    def run(self, args):
        '''Run a Git command, printing the output to STDOUT'''
        cmd = [self.git_exe] + args
        if self.verbose:
            print(f'RUN: {" ".join(_quote_arg(a) for a in cmd)}')
            print()
        subprocess.check_call(cmd, cwd=self.repo_path, env=self._get_env())

    def run_capt(self, args, input=None, binary=False, print_error=True):
        cmd = [self.git_exe] + args
        if self.verbose:
            print(f'RUN: {" ".join(_quote_arg(a) for a in cmd)}')

        if isinstance(input, str):
            input = input.encode('utf8')

        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, input=input, cwd=self.repo_path, check=False, env=self._get_env())
        if proc.returncode != 0:
            if print_error:
                for line in proc.stderr.decode('utf8', 'ignore').split('\n'):
                    print(f'GIT: {line}', file=sys.stderr)
            proc.check_returncode()

        if binary:
            return proc.stdout
        else:
            return proc.stdout.decode('utf8', 'ignore').rstrip()

    def run_paths(self, args, paths):
        args = list(args)
        args.append('--pathspec-from-file=-')
        args.append('--pathspec-file-nul')
        input = b'\x00'.join(str(path).encode('utf8', 'surrogateescape') for path in paths)
        return self.run_capt(args, input=input)

    def get_toplevel(self):
        '''Updates repo_path to be the top level path for the repository.'''
        path = Path(self.run_capt(['rev-parse', '--show-toplevel']))
        self.repo_path = path
        return path

    def get_current_commit(self):
        return self.run_capt(['rev-parse', 'HEAD'])

    def get_current_branch(self):
        branch = self.run_capt(['rev-parse', '--abbrev-ref', 'HEAD'])
        if not branch or branch == 'HEAD':
            return None
        return branch

    def list_tree(self, treeish):
        for line in self.run_capt(['ls-tree', treeish]).splitlines():
            data, fname = line.split('\t', 1)
            mode, ftype, fhash = data.split(' ', 2)
            yield mode, ftype, fhash, fname

    def get_config(self, scope=None):
        args = ['config']
        if scope is not None:
            args.append(f'--{scope}')

        args.append('--list')

        text = self.run_capt(args)
        root = {}
        for line in text.splitlines():
            key, _, val = line.partition('=')
            section, _, rest = key.partition('.')

            subsection, _, key = rest.rpartition('.')

            sect_dict = root.setdefault(section, {})
            if subsection:
                sect_dict = sect_dict.setdefault(subsection, {})

            sect_dict[key] = val

        return root

    def get_contents(self, fhash, binary=False):
        return self.run_capt(['cat-file', 'blob', fhash], binary=binary)

    def get_changed_files(self, path=None, untracked='no', ignored=None, args=()):
        changed = []

        status_args = ['--untracked-files=' + untracked]
        if ignored is not None:
            status_args.append(f'--ignored={ignored}')

        status_args.extend(args)

        if path is not None:
            status_args.append('--')
            if isinstance(path, (str, Path)):
                status_args.append(str(path))
            else:
                status_args.extend(path)

        return [row[0] for row in self.status(args)]

    def status(self, args):
        git_args = ['status', '--porcelain=v1', '-z']
        git_args.extend(args)

        text = self.run_capt(git_args)
        return self.parse_status_v1(text)

    @staticmethod
    def parse_status_v1(text):
        '''Parses the output from `git status --porcelain=v1 -z`'''
        changes = []
        itr = iter(text.split('\0'))
        for entry in itr:
            if not entry:
                continue
            code = entry[0]
            path = entry[3:]
            renamed_from = None
            if code == 'R':
                renamed_from = next(itr, None)
            changes.append((path, entry[0], entry[1], renamed_from))
        return changes


    def diff_tree(self, from_tree, to_tree='work', path=None, filter=None):
        args = ['diff-tree', '-z', '--no-renames', '--no-relative', '-r']

        if filter is not None:
            args.append('--diff-filter=' + filter)

        if to_tree in {'work', 'index'}:
            args[0] = 'diff-index'
            if to_tree == 'index':
                args.append('--cached')
            args.append(from_tree)
        else:
            args.append(from_tree)
            args.append(to_tree)

        if path is not None:
            args.append(path)

        itr = iter(self.run_capt(args).split('\0'))
        for stat in itr:
            if not stat:
                break
            old_mode, new_mode, old_hash, new_hash, status = stat.split(' ', 4)
            old_path = next(itr, None)
            new_path = next(itr, None) if status in {'C', 'R'} else old_path
            yield status, (old_mode, old_hash, path), (new_mode, new_hash, new_path)

    def _push(self, remote, commit, remote_ref, force):
        args = ['push']
        if force:
            args.append('--force')
        args.append(self.add_token(remote))
        args.append(f'{commit}:{remote_ref}')

        return self.run(args)

    def push_remote_branch(self, remote, branch, commit='HEAD', force=False):
        '''
        Push a commit directly to a remote branch.

        `remote` can be a named remote (e.g. 'origin') or a direct URL.

        `branch` is the name of the remote branch to create/update (doesn't even have to
        be a local branch).

        `commit` is a commit hash, local branch, or tag. If not specified, the current
        commit is selected.

        If `force` is True, then the branch will be updated even if it is not a
        fast-forward.
        '''
        self._push(remote, commit, f'refs/heads/{branch}', force)

    def set_remote_tag(self, remote, tag, commit='HEAD', force=False):
        '''Set a tag on a remote repository'''
        self._push(remote, commit, f'refs/tags/{tag}', force)

    def delete_remote_tag(self, remote, tag, force=False):
        '''Delete a tag from a remote repository'''
        self._push(remote, '', f'refs/tags/{tag}', force)
