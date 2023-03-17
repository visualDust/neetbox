import sys
from sys import exc_info
import inspect

def get_frame_fallback(n):
    try:
        raise Exception
    except Exception:
        frame = exc_info()[2].tb_frame.f_back
        for _ in range(n):
            frame = frame.f_back
        return frame


def load_get_frame_function():
    if hasattr(sys, "_getframe"):
        get_frame = sys._getframe
    else:
        get_frame = get_frame_fallback
    return get_frame

get_frame = load_get_frame_function()

def get_caller_identity(traceback=1):
    whom = None
    stack = inspect.stack()[2][0]
    if "self" in stack.f_locals:
        the_class = stack.f_locals["self"].__class__.__name__
        whom = str(the_class)
    else:
        the_method = stack.f_code.co_name
        previous_frame = inspect.currentframe()
        for i in range(traceback + 1):
            previous_frame = previous_frame.f_back
        (filename, line_number, function_name, lines, index) = inspect.getframeinfo(
            previous_frame
        )
        the_method = filename.split("\\")[-1].split("/")[-1]
        whom = str(the_method)
    return whom