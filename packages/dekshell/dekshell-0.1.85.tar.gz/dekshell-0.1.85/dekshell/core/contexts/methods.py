import os
import sys
import shutil
import tempfile
import glob
from pathlib import Path
from dektools.file import sure_dir, write_file, read_text, remove_path, sure_parent_dir, normal_path, \
    format_path_desc, read_file, split_ext, path_ext, where, clear_dir, \
    split_file, combine_split_files, remove_split_files, meta_split_file
from dektools.hash import hash_file
from dektools.zip import compress_files, decompress_files
from dektools.output import pprint
from dektools.net import get_available_port
from dektools.func import FuncAnyArgs
from dektools.fetch import download_file
from dektools.time import now
from ...utils.beep import sound_notify
from ..markers.invoke import InvokeMarker, GotoMarker
from ..redirect import search_bin_by_path_tree


def _is_true(x):
    if isinstance(x, str):
        x = x.lower()
    return x not in {'false', '0', 'none', 'null', '', ' ', False, 0, None, b'', b'\0'}


def _parent_dir(path, num=1):
    cursor = path
    for i in range(int(num)):
        cursor = os.path.dirname(cursor)
    return cursor


def _list_dir_one(path, file):
    path = normal_path(path)
    for item in os.listdir(path):
        result = os.path.join(path, item)
        if file is None:
            return result
        elif file:
            if os.path.isfile(result):
                return result
        else:
            if os.path.isdir(result):
                return result


def _iter_dir(path, file):
    path = normal_path(path)
    for item in os.listdir(path):
        result = os.path.join(path, item)
        if file is None:
            yield result
        elif file:
            if os.path.isfile(result):
                yield result
        else:
            if os.path.isdir(result):
                yield result


def _which(x, path=None):
    return shutil.which(x, path=path) or ''


def _where(x, path=None):
    return where(x, path=path) or ''


def _sure_and_clear(path):
    path = normal_path(path)
    sure_dir(path)
    clear_dir(path)


def _remove_path(path):
    if isinstance(path, (str, os.PathLike)):
        remove_path(path)
    else:
        for item in path:
            _remove_path(item)


def _iglob(pattern, root=None):
    if root is None:
        root = os.getcwd()
    else:
        root = normal_path(root)
    if isinstance(pattern, str):
        cache = None
        pattern = [pattern]
    else:
        if len(pattern) > 1:
            cache = set()
        else:
            cache = None
    for p in pattern:
        for item in glob.iglob(p, root_dir=root):
            pa = os.path.join(root, item)
            if cache is not None:
                if pa in cache:
                    continue
                cache.add(pa)
            yield pa


path_common_methods = {
    'cd': os.chdir,
    'cwd': lambda: os.getcwd(),
    'which': _which,
    'where': _where,
    'pybin': lambda x, p=None: search_bin_by_path_tree(p or os.getcwd(), x, False),
}

default_methods = {
    'echo': lambda *x, **y: print(*x, **dict(flush=True) | y),
    'echos': lambda *x, **y: print(*x, **dict(end='', flush=True) | y),
    'echox': lambda *x, **y: print(*x, **dict(file=sys.stderr, flush=True) | y),
    'pp': pprint,
    'now': now,
    'Path': Path,
    'path': {
        **path_common_methods,
        'exists': os.path.exists,
        'parent': _parent_dir,
        'abs': normal_path,
        'fullname': os.path.basename,
        'name': lambda x: split_ext(x)[0],
        'ext': path_ext,
        'desc': format_path_desc,
        'md': lambda x: sure_dir(normal_path(x)),
        'mdp': lambda x: sure_parent_dir(normal_path(x)),
        'mdt': lambda x=None: tempfile.mkdtemp(prefix=x),
        'mdc': _sure_and_clear,

        'lsa': lambda path='.', file=None: list(_iter_dir(path, file)),
        'lso': lambda path='.', file=None: _list_dir_one(path, file) or '',
        'ls': lambda x='.': os.listdir(x),

        'iglob': _iglob,
        'glob': lambda *args, **kwargs: list(_iglob(*args, **kwargs)),

        'rm': _remove_path,
        'wf': write_file,
        'rt': read_text,
        'rf': read_file,

        'sf': split_file,
        'sfr': remove_split_files,
        'sfm': meta_split_file,
        'sfc': combine_split_files,

        'hash': lambda x, name='sha256', args=None: hash_file(name, x, args=args),
    },
    **path_common_methods,

    'compress': compress_files,
    'decompress': decompress_files,

    'func': FuncAnyArgs,

    'fetch': download_file,

    'me': lambda x: x,
    'first': lambda x: x[0] if x else None,
    'true': lambda x=True: _is_true(x),
    'false': lambda x=False: not _is_true(x),

    'equal': lambda x, y: x == y,
    'notequal': lambda x, y: x != y,
    'beep': lambda x=True: sound_notify(x),

    'invoke': lambda __not_use_this_var_name__, *args, **kwargs: InvokeMarker.execute_file(
        None, __not_use_this_var_name__, args, kwargs),
    'goto': lambda __not_use_this_var_name__, *args, **kwargs: GotoMarker.execute_file(
        None, __not_use_this_var_name__, args, kwargs),

    'net': {
        'port': get_available_port
    },
}
