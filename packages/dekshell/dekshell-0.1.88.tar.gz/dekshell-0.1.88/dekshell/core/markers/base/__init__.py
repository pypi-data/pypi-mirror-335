import os
import re
import functools
from dektools.str import deep_format, split_table_line, shlex_split
from dektools.common import classproperty
from dektools.shell import shell_output, shell_wrapper, shell_exitcode
from ....utils.serializer import serializer
from ....utils.cmd import cmd2ak

cmd_call_prefix_simple = '>'
cmd_call_prefix = cmd_call_prefix_simple * 2
cmd_call_prefix_chain = cmd_call_prefix_simple * 3
cmd_call_eval_prefix = '='
cmd_call_eval_escape = '\\'


class MarkerBase:
    tag_head = None
    tag_head_args = None
    tag_head_re = None
    tag_head_re_args = None
    tag_tail = None
    branch_set = set()

    var_name_anonymous = '_'

    trans_marker_command_rc_silence = '<<<'
    trans_marker_command_rc = '<<'
    trans_marker_command_output = '<'
    trans_marker_decode = '//'
    trans_marker_encode = '/'
    trans_marker_env = '$$'
    trans_marker_env_full = '$'
    trans_marker__set = '|'.join((re.escape(x) for x in [
        trans_marker_command_rc_silence,
        trans_marker_command_rc,
        trans_marker_command_output,
        trans_marker_decode,
        trans_marker_encode,
        trans_marker_env,
        trans_marker_env_full,
    ]))
    trans_marker__as_var = '='
    trans_marker__ignore = '?'
    trans_marker__begin = "{"
    trans_marker__end = "}"
    trans_marker__escape = "\\"

    VALUE_UNSET = type('Unset', (), {})

    @classmethod
    def get_tag_match(cls):
        if cls.tag_head is not None:
            s = cls.tag_head if cls.tag_head_args is None else cls.tag_head % cls.tag_head_args
        else:
            s = None
        if cls.tag_head_re is not None:
            r = cls.tag_head_re if cls.tag_head_re_args is None else cls.tag_head_re % cls.tag_head_re_args
        else:
            r = None
        return s, r

    def recognize(self, command):
        command = self.strip(command)
        s, r = self.get_tag_match()
        if s is not None:
            if command.startswith(s):
                rule = re.compile('[0-9a-zA-Z_]')
                return not (s and rule.match(s[-1]) and rule.match(command[len(s):len(s) + 1]))
            return False
        elif r is not None:
            return bool(re.match(r, command))
        return False

    def transform(self, parent):
        return self

    def bubble_continue(self, context, marker_set, marker_node_self, marker_node_target):
        return None

    def execute(self, context, command, marker_node, marker_set):
        pass

    def execute_result(self, result):
        pass

    def exit(self):
        raise ExitException()

    def ret(self, value):
        raise QuitContextException(value)

    def set_var(self, context, array, index, value):
        self.set_var_raw(context, self.get_item(array, index, self.var_name_anonymous), value)

    @staticmethod
    def set_var_raw(context, name, value):
        context.add_variable(name, value)

    @staticmethod
    def remove_var(context, name):
        context.remove_variable(name)

    @classmethod
    def cmd_call_parse(cls, context, s, simple):
        if simple:
            argv = cls.split_raw(s, 1)
            args = argv[1:]
            kwargs = {}
        else:
            argv = cls.split(s)
            args, kwargs = cls.cmd2ak(argv[1:])
            args, kwargs = cls.var_map_batch(context, *args, **kwargs)
        func = argv[0]
        return func, args, kwargs

    @classmethod
    def cmd_call(cls, context, s, simple):
        func, args, kwargs = cls.cmd_call_parse(context, s, simple)
        func = cls.eval(context, func)
        return func(*args, **kwargs)

    @classmethod
    def translate(cls, context, s):
        return cls._translate(context, s)

    @classmethod
    def _translate(cls, context, s):
        def handler(expression, marker, _):
            as_var = False
            ignore = False
            m = re.match(
                r'(%s|%s)*' % (re.escape(cls.trans_marker__as_var), re.escape(cls.trans_marker__ignore)), expression)
            if m:
                index = m.span()[1]
                mm = expression[:index]
                as_var = cls.trans_marker__as_var in mm
                ignore = cls.trans_marker__ignore in mm
                expression = expression[index:]
            value = handler_core(expression, ignore, marker)
            if as_var:
                return context.add_variable_temp(value)
            return value

        def evaluate(expression, ignore, default):
            try:
                return cls.eval_mixin(context, expression, False)
            except NameError:
                if ignore:
                    return default
                else:
                    raise

        def handler_core(expression, ignore, marker):
            key = marker[len(cls.trans_marker__begin):]
            if key.startswith(cls.trans_marker_command_rc_silence):
                return shell_exitcode(expression, env=context.environ_full())
            elif key.startswith(cls.trans_marker_command_rc):
                return shell_wrapper(expression, check=False, env=context.environ_full())
            elif key.startswith(cls.trans_marker_command_output):
                return shell_output(expression, env=context.environ_full())
            elif key.startswith(cls.trans_marker_env):
                return os.getenv(expression.strip(), default_value)
            elif key.startswith(cls.trans_marker_env_full):
                return context.get_env(expression.strip(), default_value)
            elif key.startswith(cls.trans_marker_decode):
                value = evaluate(expression, ignore, empty_value)
                if value is empty_value:
                    return default_value
                return serializer.load(value)
            elif key.startswith(cls.trans_marker_encode):
                value = evaluate(expression, ignore, empty_value)
                if value is empty_value:
                    return default_value
                return serializer.dump(value)
            else:
                return evaluate(expression, ignore, default_value)

        empty_value = object()
        default_value = ''

        translate = deep_format(
            s, f"{re.escape(cls.trans_marker__begin)}({cls.trans_marker__set})?",
            re.escape(cls.trans_marker__end), handler, cls.trans_marker__escape)
        return translate

    @classproperty
    @functools.lru_cache(None)
    def final_branch_set(cls):
        return {cls if x is None else x for x in cls.branch_set}

    @staticmethod
    def get_item(array, index, default=None):
        if array:
            try:
                return array[index]
            except IndexError:
                pass
        return default

    @staticmethod
    def strip(command):
        return command.strip()

    @staticmethod
    def split(command):
        return shlex_split(command)

    @staticmethod
    def split_raw(command, maxsplit=None, sep=None):
        return split_table_line(command, maxsplit, sep)

    @staticmethod
    def eval(context, s, v=None):
        if not s:
            return None
        return eval(s, context.variables_full() | (v or {}))

    @classmethod
    def eval_mixin(cls, context, expression, translate=True):
        expression = expression.lstrip()
        if expression.startswith(cmd_call_prefix_chain):
            if translate:
                expression = cls._translate(context, expression)
            expression = expression[len(cmd_call_prefix_chain):]
            index = re.search(
                r"%s|%s" % (re.escape(cmd_call_prefix_simple), re.escape(cmd_call_eval_prefix)), expression).span()[0]
            funcs = cls.split_raw(expression[:index])
            value = cls.eval_mixin(context, expression[index:], False)
            for func in reversed(funcs):
                if func:
                    value = cls.eval(context, func)(value)
            return value
        elif expression.startswith(cmd_call_prefix):
            if translate:
                expression = cls._translate(context, expression)
            return cls.cmd_call(context, expression[len(cmd_call_prefix):], False)
        elif expression.startswith(cmd_call_prefix_simple):
            if translate:
                expression = cls._translate(context, expression)
            return cls.cmd_call(context, expression[len(cmd_call_prefix_simple):], True)
        else:
            if expression.startswith(cmd_call_eval_prefix):
                expression = expression[len(cmd_call_eval_prefix):]
            return cls.eval(context, expression)

    @staticmethod
    def eval_lines(context, s, v=None):
        globals_ = context.variables_full() | (v or {})
        locals_ = {}
        exec(s, globals_, locals_)
        return locals_

    @classmethod
    def var_map(cls, context, s):
        if s.startswith(cmd_call_eval_prefix):
            return cls.eval(context, s[len(cmd_call_eval_prefix):])
        else:
            if s.startswith(f'{cmd_call_eval_escape}{cmd_call_eval_prefix}'):
                s = s[len(cmd_call_eval_escape):]
            return s

    @classmethod
    def var_map_batch(cls, context, *args, **kwargs):
        return [cls.var_map(context, x) for x in args], {k: cls.var_map(context, v) for k, v in kwargs.items()}

    @staticmethod
    def cmd2ak(argv):
        return cmd2ak(argv)


class EndMarker(MarkerBase):
    tag_head = "end"


class BreakMarker(MarkerBase):
    tag_head = "break"


class ContinueMarker(MarkerBase):
    tag_head = "continue"


class TransformerMarker(MarkerBase):
    def __init__(self, targets):
        super().__init__()
        self.targets = targets

    def recognize(self, command):
        return self.targets[0].recognize(command)

    def transform(self, parent):
        for target in self.targets:
            if target.is_type(*parent.final_branch_set):
                return target
        return self.targets[0]

    @classmethod
    def inject(cls, markers):
        records_markers = {}
        records_index = {}
        records_target = set()
        for i, marker in enumerate(markers):
            match = marker.get_tag_match()
            if marker in records_markers:
                records_markers[match].append(marker)
            else:
                records_markers[match] = []
            if len(records_markers[match]) > 1:
                records_target.add(match)
            if marker not in records_index:
                records_index[match] = i
        offset = 0
        for match in sorted(records_target, key=lambda x: records_index[x]):
            index = records_index[match] + offset
            markers.insert(index, cls(records_markers[match]))
            offset += 1
        return markers


class MarkerWithEnd(MarkerBase):
    tag_tail = EndMarker

    def get_inner_content(self, context, marker_node):
        commands = []
        marker_node.walk(lambda node, depth: commands.extend([] if depth == 0 else [node.command]))
        text = '\n'.join(commands)
        return self.translate(context, text)

    def eval_codes(self, context, code):
        if not code:
            return None
        codes = code.split('\n')
        codes[-1] = f"_ = {codes[-1]}"
        return self.eval_lines(context, '\n'.join(codes))['_']

    def find_node(self, marker_node_list, reverse=False, node_set=None):
        if node_set is None:
            node_set = self.final_branch_set
        if reverse:
            target = reversed(marker_node_list)
        else:
            target = marker_node_list
        index = None
        for i, child in enumerate(target):
            if reverse and child.is_type(self.tag_tail):
                break
            if child.is_type(*node_set):
                index = i
                break
        if index is not None and reverse:
            return len(marker_node_list) - 1 - index
        return index


class MarkerNoTranslator(MarkerBase):
    def translate(self, context, s):
        return s


class MarkerShellBase(MarkerBase):
    shell_cls = None

    def execute(self, context, command, marker_node, marker_set):
        command = self.strip(command)
        if command:
            self.execute_core(context, command, marker_node, marker_set)

    @classmethod
    def execute_core(cls, context, command, marker_node, marker_set, kwargs=None):
        kwargs = (marker_node.payload or {}) | (kwargs or {})
        return marker_set.shell_cmd(command, cls.shell_cls(kwargs), env=context.environ_full())


class ExceptionShell(Exception):
    pass


class ExitException(ExceptionShell):
    pass


class QuitContextException(ExceptionShell):
    pass
