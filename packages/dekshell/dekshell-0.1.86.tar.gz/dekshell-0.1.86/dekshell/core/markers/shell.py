import os
from .base import MarkerWithEnd
from .empty import EmptyMarker


class ShellMarker(MarkerWithEnd):
    tag_head = "shell"
    target_marker_cls = EmptyMarker

    def execute(self, context, command, marker_node, marker_set):
        argv = self.split_raw(command, 1)
        config = self.get_item(argv, 1, '').strip()
        if config:
            config = eval(f'dict({config})', {'environ': context.environ_full()})
        else:
            config = None
        marker = marker_set.find_marker_by_cls(self.target_marker_cls)
        result = []
        for child in marker_node.children:
            if child.is_type(self.target_marker_cls):
                node = marker_set.node_cls(
                    marker,
                    child.command,
                    child.index,
                    marker_node,
                    payload=config
                )
                result.append(node)
            else:
                result.append(child)
        return result
