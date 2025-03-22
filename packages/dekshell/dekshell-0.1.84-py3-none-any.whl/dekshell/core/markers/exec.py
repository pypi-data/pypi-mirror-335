from .base import MarkerBase, MarkerWithEnd, MarkerNoTranslator, cmd_call_prefix, cmd_call_prefix_simple, \
    cmd_call_prefix_chain
from .empty import EmptyMarker


class ExecMarker(MarkerNoTranslator):
    tag_head = '='

    def execute(self, context, command, marker_node, marker_set):
        args = self.split_raw(command, 1, self.tag_head)
        if args[1]:
            self.eval(context, args[1])


class ExecLinesMarker(MarkerWithEnd, MarkerNoTranslator):
    tag_head = '=='

    def execute(self, context, command, marker_node, marker_set):
        code = self.get_inner_content(context, marker_node)
        self.eval_lines(context, code)
        return []


class ExecLinesUpdateMarker(MarkerWithEnd, MarkerNoTranslator):
    tag_head = '==='

    def execute(self, context, command, marker_node, marker_set):
        code = self.get_inner_content(context, marker_node)
        context.update_variables(self.eval_lines(context, code))
        return []


class ExecCmdcallMarker(MarkerBase):
    tag_head = cmd_call_prefix_simple

    def execute(self, context, command, marker_node, marker_set):
        self.eval_mixin(context, command, False)


class ExecCmdcallLinesMarker(MarkerWithEnd):
    tag_head = f'{cmd_call_prefix_chain}{cmd_call_prefix_simple}'
    cmd_call_marker_cls = ExecCmdcallMarker
    targets_marker_cls = (EmptyMarker,)

    def execute(self, context, command, marker_node, marker_set):
        marker = marker_set.find_marker_by_cls(self.cmd_call_marker_cls)
        result = []
        for child in marker_node.children:
            if child.is_type(*self.targets_marker_cls):
                node = marker_set.node_cls(
                    marker,
                    self.cmd_call_marker_cls.tag_head + ' ' + child.command,
                    child.index,
                    marker_node,
                    child.command
                )
                result.append(node)
            else:
                result.append(child)
        return result
