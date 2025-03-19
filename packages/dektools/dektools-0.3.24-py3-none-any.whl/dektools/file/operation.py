import os
import tempfile
import shutil
import codecs
import filecmp
from io import BytesIO
from ..common import ns2datetime
from ..format import format_file_size
from ..str import Fragment, comment_code
from .path import normal_path, new_empty_path

DEFAULT_VALUE = type('default_value', (), {})


def write_file(
        filepath,
        s=None, b=None, sb=None, a=None,
        m=None, mi=None,
        c=None, ci=None,
        ma=None, mo=None, mie=None,
        t=False,
        encoding='utf-8'):
    is_link = os.path.islink(filepath) if filepath else False
    if not is_link and filepath and not t and a is None and \
            mi is None and ci is None and ma is None and mo is None and mie is None:
        if os.path.exists(filepath):
            remove_path(filepath)
        else:
            sure_dir(os.path.dirname(normal_path(filepath)))
    if t:
        pt = tempfile.mkdtemp()
        if s is not None or b is not None or sb is not None:
            fp = os.path.join(pt, filepath) if filepath else new_empty_path(pt, 'temp')
            write_file(fp, s=s, b=b, sb=sb)
        else:
            fp = os.path.join(pt, filepath or os.path.basename(m or mi or c or ci or ma or mo or mie))
            write_file(fp, m=m, mi=mi, c=c, ci=ci, ma=ma, mo=mo, mie=mie)
        return fp
    elif s is not None:
        if is_link:
            filepath = os.path.realpath(filepath)
        with codecs.open(filepath, 'a' if a else 'w', encoding=encoding) as f:
            if not a and is_link:
                f.truncate()
            return f.write(s)
    elif b is not None:
        if is_link:
            filepath = os.path.realpath(filepath)
        with open(filepath, 'r+b' if a else 'wb') as f:
            if a:
                f.seek(os.path.getsize(filepath))
            elif is_link:
                f.truncate()
            f.write(b)
    elif sb is not None:
        if isinstance(sb, str):
            write_file(filepath, s=sb, a=a)
        else:
            write_file(filepath, b=sb, a=a)
    elif c is not None:
        filepath_temp = new_empty_path(filepath)
        if os.path.exists(filepath_temp):
            os.remove(filepath_temp)
        if os.path.isdir(c):
            shutil.copytree(c, filepath_temp)
        else:
            shutil.copyfile(c, filepath_temp)
        shutil.move(filepath_temp, filepath)
    elif ci is not None:
        if os.path.exists(ci):
            write_file(filepath, c=ci)
    elif m is not None:
        shutil.move(m, filepath)
    elif mi is not None:
        if os.path.exists(mi):
            write_file(filepath, m=mi)
    elif ma is not None:
        merge_assign(sure_dir(filepath), ma)
    elif mo is not None:
        merge_overwrite(sure_dir(filepath), mo)
    elif mie is not None:
        merge_ignore_exists(sure_dir(filepath), mie)
    else:
        raise TypeError('s, b, c, ci, m, mi, ma, mo, mie is all empty')


def read_file(filepath, default=DEFAULT_VALUE):
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def write_file_(filepath, content):
    sure_dir(os.path.dirname(normal_path(filepath)))
    with open(filepath, 'wb') as f:
        f.write(content)


def read_chunked(filepath, chunked_size=64 * 2 ** 10, default=DEFAULT_VALUE):
    if os.path.isfile(filepath):
        with open(filepath, 'rb') as f:
            for chunk in iter(lambda: f.read(chunked_size), b""):
                yield chunk
    else:
        if default is not DEFAULT_VALUE:
            yield default
        else:
            raise FileNotFoundError(filepath)


def read_text(filepath, default=DEFAULT_VALUE, encoding='utf-8'):  # default: str | type
    if filepath and os.path.isfile(filepath):
        with codecs.open(filepath, encoding=encoding) as f:
            return f.read()
    else:
        if default is not DEFAULT_VALUE:
            return default
        else:
            raise FileNotFoundError(filepath)


def iter_file_obj_lines(file):
    for line in file:
        if line[-1] == '\n':
            yield line[:-1]
        else:
            yield line


def iter_lines(filepath, default=DEFAULT_VALUE, encoding='utf-8'):  # default: str | type
    if filepath and os.path.isfile(filepath):
        with codecs.open(filepath, encoding=encoding) as f:
            yield from iter_file_obj_lines(f)
    else:
        if default is not DEFAULT_VALUE:
            yield from default.splitlines()
        else:
            raise FileNotFoundError(filepath)


def write_text(filepath, content, encoding='utf-8'):
    sure_dir(os.path.dirname(normal_path(filepath)))
    with codecs.open(filepath, 'w', encoding=encoding) as f:
        return f.write(content)


def read_lines(filepath, default=DEFAULT_VALUE, encoding='utf-8', skip_empty=False, strip=True, trace=False):
    for i, line in enumerate(iter_lines(filepath, default=default, encoding=encoding)):
        if strip:
            line = line.strip()
        if skip_empty and not line:
            continue
        yield (filepath, i + 1, line) if trace else line


def remove_path(path, ignore=False):
    try:
        if os.path.isdir(path):
            shutil.rmtree(path)
        elif os.path.isfile(path):
            os.remove(path)
        return True
    except PermissionError as e:
        if not ignore:
            raise e from e
        return False


def real_path(path):
    def real_file(p):
        if os.path.islink(p):
            pp = os.path.realpath(p)
            os.remove(p)
            shutil.copyfile(pp, p)

    if os.path.isdir(path):
        for root, _, filenames in os.walk(path):
            for filename in filenames:
                real_file(os.path.join(root, filename))
    elif os.path.isfile(path):
        real_file(path)


def replace_file(entries, reverse=False):
    for path, replace in entries.items():
        content = read_text(path)
        content = Fragment.replace_safe_again(content, replace, reverse)
        if content is not None:
            write_file(path, sb=content)


def comment_file(entries, comment, reverse=False):
    for path, replace in entries.items():
        content = read_text(path)
        content = Fragment.replace_safe_again(
            content, [[code, comment_code(code, comment, again=True)][::-1 if reverse else 1] for code in replace])
        if content is not None:
            write_file(path, sb=content)


def clear_dir(path, ignore=False):
    for file in os.listdir(path):
        remove_path(os.path.join(path, file), ignore)


def merge_dir(dest, src):
    for fn in os.listdir(src):
        write_file(os.path.join(dest, fn), ci=os.path.join(src, fn))


def copy_path(src, dest):
    remove_path(dest)
    if os.path.isdir(src):
        shutil.copytree(src, dest)
    elif os.path.isfile(src):
        shutil.copyfile(src, dest)


def copy_file_stable(src, dest, cache=None):
    sure_dir(os.path.dirname(normal_path(dest)), cache)
    with open(dest, 'wb') as f:
        for chunk in read_chunked(src):
            f.write(chunk)


def sure_parent_dir(path, cache=None):
    return sure_dir(os.path.dirname(path), cache)


def sure_dir(path, cache=None):
    if cache and path in cache:
        return path
    if not os.path.exists(path):
        os.makedirs(path)
        if cache is not None:
            cache.add(path)
    return path


def sure_read(path_or_content):
    if isinstance(path_or_content, (bytes, memoryview)):
        return BytesIO(path_or_content)
    else:
        return path_or_content


def content_cmp(a, b):
    return filecmp.cmp(a, b, False)


def list_relative_path(src):
    def walk(p):
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if os.path.isfile(fp):
                result[fp[len(str(src)) + 1:]] = fp
            elif os.path.isdir(fp):
                walk(fp)

    result = {}
    if os.path.isdir(src):
        walk(src)
    return result


def iter_relative_path(src):
    def walk(p):
        for fn in os.listdir(p):
            fp = os.path.join(p, fn)
            if os.path.isfile(fp):
                yield fp[len(str(src)) + 1:], fp
            elif os.path.isdir(fp):
                yield from walk(fp)

    if os.path.isdir(src):
        yield from walk(src)


def iter_relative_path_complete(src):
    def walk(p):
        fns = os.listdir(p)
        if fns:
            for fn in fns:
                fp = os.path.join(p, fn)
                if os.path.isfile(fp):
                    yield fp[len(str(src)) + 1:], fp, True
                elif os.path.isdir(fp):
                    yield from walk(fp)
        else:
            yield p[len(str(src)) + 1:], p, False

    if os.path.isdir(src):
        yield from walk(src)


def list_dir(path, full=False):
    if os.path.isdir(path):
        for item in os.listdir(path):
            fullpath = os.path.join(path, item)
            if full:
                yield fullpath, item
            else:
                yield fullpath


def merge_assign(dest, src):
    cache = set()
    for rp, fp in iter_relative_path(src):
        copy_file_stable(fp, os.path.join(dest, rp), cache)


def merge_ignore_exists(dest, src):
    cache = set()
    for rp, fp in iter_relative_path(src):
        p = os.path.join(dest, rp)
        if not os.path.exists(p):
            copy_file_stable(fp, p, cache)


def merge_overwrite(dest, src):  # Causing minimal impact
    cache = set()
    src_info = list_relative_path(src)
    for rp, fp in src_info.items():
        copy_file_stable(fp, os.path.join(dest, rp), cache)
    for rp, fp in iter_relative_path(dest):
        if rp not in src_info:
            remove_path(fp)


def merge_move(dest, src):
    cache = set()
    for rp, fp in iter_relative_path(src):
        dp = os.path.join(dest, rp)
        remove_path(dp)
        sure_dir(os.path.dirname(dp), cache)
        os.rename(fp, dp)


def remove_empty_dir(path):
    empty_set = set()
    for root, dirs, filenames in os.walk(path, topdown=False):
        if not filenames and all(os.path.join(root, d) in empty_set for d in dirs):
            empty_set.add(root)
            os.rmdir(root)


def desc_path(path):
    if os.path.isfile(path):
        stat = os.stat(path)
        return stat.st_size, stat.st_ctime_ns, stat.st_mtime_ns
    elif os.path.isdir(path):
        e, f, g = 0, 0, 0
        count = 0
        for base, _, files in os.walk(path):
            for file in files:
                p = os.path.join(base, file)
                stat = os.stat(p)
                e += stat.st_size
                f = max(stat.st_ctime_ns, f)
                g = max(stat.st_mtime_ns, g)
                count += 1
        return e, f, g, count


def format_path_desc(path, sep=None):
    def ts(t):
        return ns2datetime(t).strftime('%Y-%m-%d/%H:%M:%S')

    def fs(a, b, c, d=None):
        s = f"{format_file_size(a)}{sep}{ts(b)}{sep}{ts(c)}"
        if d is not None:
            s = f'{s}{sep}{d}'
        return s

    sep = ' - ' if sep is None else sep
    desc = desc_path(path)
    if desc:
        return fs(*desc)
    return ''
