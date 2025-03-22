import os
import sys
import shutil
import tempfile
from pathlib import Path
from sysconfig import get_paths
from importlib import metadata
from dektools.module import ModuleProxy
from dektools.time import DateTime
from ...utils.serializer import serializer
from ..redirect import shell_name

current_shell = shutil.which(shell_name, path=get_paths()['scripts'])


def make_shell_properties(shell):
    return {
        'shell': shell,
        'sh': {
            'rf': f'{shell} rf',
            'rfc': f'{shell} rfc',
            'rs': f'{shell} rs',
        },
    }


package_name = __name__.partition(".")[0]
path_home = os.path.expanduser('~')
is_on_win = os.name == "nt"
path_root = path_home[:path_home.find(os.sep)] if is_on_win else os.sep


class _Env:
    def __getattr__(self, item):
        return os.environ.get(item.upper(), '')

    def __getitem__(self, item):
        return os.environ[item.upper()]

    def __contains__(self, item):
        return item.upper() in os.environ


default_properties = {
    'meta': {
        'name': package_name,
        'version': metadata.version(package_name)
    },
    'python': sys.executable,
    **make_shell_properties(current_shell),
    'os': {
        'pid': os.getpid(),
        'win': is_on_win,
        'ps': os.pathsep,
    },
    'path': {
        'root': Path(path_root),
        'home': Path(path_home),
        'temp': Path(tempfile.gettempdir()),
        'sep': os.sep
    },
    'obj': serializer,
    'mp': ModuleProxy(),
    'date': DateTime(),
    'envx': _Env(),
}
