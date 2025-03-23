from dektools.shell import shell_command
from .base import MarkerShellBase


class ShellCommand:
    def __init__(self, kwargs):
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs = kwargs | self.kwargs
        return self.shell(*args, **kwargs)

    def shell(self, *args, **kwargs):
        return shell_command(*args, **kwargs)


class MarkerShell(MarkerShellBase):
    tag_head = ""
    shell_cls = ShellCommand


class EmptyMarker(MarkerShell):
    pass
