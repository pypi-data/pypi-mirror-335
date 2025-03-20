import subprocess
from dektools.shell import shell_timeout
from .empty import EmptyMarker, ShellCommand


class TimeoutShellCommand(ShellCommand):
    def shell(self, command, timeout=None, env=None, **kwargs):
        try:
            return shell_timeout(command, timeout, env=env, check=True) or None
        except subprocess.CalledProcessError as e:
            return e


class TimeoutMarker(EmptyMarker):
    tag_head = "timeout"

    shell_cls = TimeoutShellCommand

    def execute(self, context, command, marker_node, marker_set):
        _, timeout, command = self.split_raw(command, 2)
        if command:
            self.execute_core(context, command, marker_node, marker_set, dict(timeout=int(float(timeout))))
