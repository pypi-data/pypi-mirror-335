import os
import uuid
from itertools import chain


def join_path(*args):
    return os.path.normpath(os.path.join(*(args[0], *(x.strip('\\/') for x in args[1:]))))


def normal_path(path, unix=False):
    path = os.path.normpath(os.path.abspath(os.path.expanduser(os.fspath(path))))
    if unix and os.name == 'nt':
        path = path.replace('\\', '/')
    return path


def new_empty_path(*paths):
    while True:
        np = f"{os.path.join(*paths)}.{uuid.uuid4().hex}"
        if not os.path.exists(np):
            return np


def split_ext(path):
    file, ext = os.path.splitext(path)
    if not ext and file.startswith('.'):
        return '', file
    return file, ext


def path_ext(path):
    return split_ext(path)[-1]


def multi_ext(path, limit=None, case=False):
    filename = os.path.basename(path)
    result = []
    while True:
        index = filename.rfind('.')
        if index != -1:
            ext = filename[index:]
            if case is None:
                pass
            elif case:
                ext = ext.upper()
            else:
                ext = ext.lower()
            result.insert(0, ext)
            filename = filename[:index]
            if limit is not None and len(result) >= limit:
                break
        else:
            break
    return filename, result


def where(x, path=None):
    if path:
        paths = [path]
    else:
        paths = chain(iter([os.getcwd()]), iter(os.environ['PATH'].split(os.pathsep)))
    for p in paths:
        fp = os.path.join(p, x)
        if os.path.exists(fp):
            return fp
    return None
