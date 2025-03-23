from ..plugin import get_markers_from_modules
from .base import EndMarker, BreakMarker, ContinueMarker
from .var import *
from .env import *
from .if_ import *
from .while_ import *
from .for_ import *
from .define import *
from .comment import *
from .invoke import *
from .function import *
from .exec import *
from .echo import *
from .pip_ import *
from .shell import *
from .redirect import *
from .timout import *
from .empty import *


def generate_markers(*args, **kwargs):
    return [
        *args,
        *get_markers_from_modules(**kwargs),
        ErrorEchoMarker, EchoNoWrapMarker, EchoMarker,
        DelVarMarker,
        ExecLinesUpdateMarker, ExecLinesMarker, ExecMarker, ExecCmdcallLinesMarker, ExecCmdcallMarker,
        EnvShellMarker, EnvMarker,
        IfMarker, IfElifMarker, IfElseMarker,
        WhileMarker,
        ForMarker, ForElseMarker,
        DefineMarker,
        GotoMarker, InvokeMarker,
        FunctionMarker, CallMarker, ReturnMarker, EnvGlobalMarker, EnvNonlocalMarker,
        VarGlobalMarker, VarNonlocalMarker,
        EndMarker, BreakMarker, ContinueMarker,
        CommentMultiLineMarker, CommentMarker, CommentShebangMarker, CommentConfigMarker,
        PipMarker,
        ShellMarker,
        RedirectMarker, ShiftMarker,
        TimeoutMarker,
        IgnoreMarker,
        AssignCallMarker, AssignInvokerMarker, AssignGotoMarker, AssignTimeoutMarker,
        AssignExecMarker, AssignEvalMarker, AssignCmdcallMarker,
        AssignMultiLineRawStrMarker, AssignMultiLineStrMarker, AssignRawStrMarker, AssignStrMarker,
        EmptyMarker,  # must be at the tail
    ]
