import re
import sys
from dektools.escape.str import str_escape_one_type


def cmd2ak(argv):  # arg0 arg-\-1 k0--kwarg0 k1--kwarg1
    args = []
    kwargs = {}
    for x in argv:
        if re.match(r'[^\W\d]\w*--', x):
            k, v = x.split('--', 1)
            kwargs[k] = v
        else:
            args.append(str_escape_one_type(x, '-', '-'))
    return args, kwargs


def ak2cmd(args, kwargs=None):
    result = []
    if args:
        for arg in args:
            arg = arg.replace('--', r'-\-')
            result.append(f'"{arg}"')
    if kwargs:
        for k, v in kwargs.items():
            result.append(f'"{k}--{v}"')
    return ' '.join(result)


def pack_context(args, kwargs):
    return {f'__arg{i}': arg for i, arg in enumerate(args)} | {'__args': args, '__kwargs': kwargs} | kwargs


def pack_context_argv():
    return {f"__argv{i}": x for i, x in enumerate(sys.argv)} | {'__argv': sys.argv}


def pack_context_full(args=None, kwargs=None):
    return pack_context(args or [], kwargs or {}) | pack_context_argv()
