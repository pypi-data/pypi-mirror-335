import os
import configparser
from io import BytesIO
from itertools import chain
from collections import OrderedDict
from .file import read_text, remove_path
from .shell import shell_wrapper


def git_parse_modules(s):
    cp = configparser.ConfigParser()
    if isinstance(s, str):
        cp.read_string(s)
    else:
        if isinstance(s, bytes):
            s = BytesIO(s)
        cp.read_file(s)
    result = OrderedDict()
    for section in cp.sections():
        submodule = section.split(' ', 1)[-1][1:-1]
        options = result[submodule] = OrderedDict()
        for k in cp.options(section):
            v = cp.get(section, k)
            options[k] = v
    return result


def git_clean_dir(path):
    modules = read_text(os.path.join(path, '.gitmodules'), default=None)
    if modules:
        subs = (os.path.join(path, v['path']) for v in git_parse_modules(modules).values())
    else:
        subs = range(0)
    for p in chain(iter([path]), iter(subs)):
        path_git = os.path.join(p, '.git')
        if os.path.exists(path_git):
            shell_wrapper(f'git -C "{p}" clean -dfX')
            remove_path(path_git)
        else:
            print(f'Skip `{p}` as it is not a git folder')


def git_fetch_min(url, tag, path):
    shell_wrapper(f'git -C "{path}" clone --depth 1 --branch {tag} {url} .')
    shell_wrapper(f'git -C "{path}" submodule update --depth 1 --init --recursive')
