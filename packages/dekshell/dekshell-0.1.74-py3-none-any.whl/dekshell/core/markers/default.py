from .base import MarkerNoTranslator


class DefaultMarker(MarkerNoTranslator):
    tag_head = "default"

    def execute(self, context, command, marker_node, marker_set):
        args = self.split_raw(command, 2)
        var_name = args[1]
        try:
            self.eval(context, var_name)
        except NameError:
            expression = self.get_item(args, 2)
            if expression:
                result = self.eval_mixin(context, expression)
            else:
                result = ''
            self.set_var_raw(context, var_name, result)
