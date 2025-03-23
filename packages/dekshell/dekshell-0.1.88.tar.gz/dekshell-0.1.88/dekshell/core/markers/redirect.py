from dektools.shell import shell_wrapper
from dektools.attr import DeepObject
from ...core.redirect import redirect_shell_by_path_tree
from ..contexts.properties import make_shell_properties, current_shell
from .base import MarkerBase


class RedirectMarker(MarkerBase):
    tag_head = "redirect"

    def execute(self, context, command, marker_node, marker_set):
        path_dir = self.split_raw(command, 1)[1]
        path_shell = redirect_shell_by_path_tree(path_dir)
        if path_shell:
            shell_properties = make_shell_properties(path_shell)
            if shell_properties['shell'] != current_shell:
                shell = shell_properties['sh']['rf']
                shell_wrapper(f'{shell} {self.eval(context, "fp")}', env=context.environ_full())
                self.exit()


class ShiftMarker(MarkerBase):
    tag_head = "shift"

    def execute(self, context, command, marker_node, marker_set):
        path_dir = self.split_raw(command, 1)[1]
        path_shell = redirect_shell_by_path_tree(path_dir)
        if path_shell:
            context.update_variables(DeepObject(make_shell_properties(path_shell)).__dict__)
