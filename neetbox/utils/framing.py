# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230319

import inspect
import types
from os import path
from typing import Union


def get_frame_traceback(traceback=1):
    stack = inspect.stack()
    traceback = len(stack) - 1 if traceback >= len(stack) else traceback
    return stack[traceback]


def get_frame_func_name_traceback(traceback=1):
    frame = get_frame_traceback(traceback + 1)
    func = frame.function
    return None if func == "<module>" else func


def get_frame_class_traceback(traceback=1):
    frame = get_frame_traceback(traceback + 1)
    _locals = frame[0].f_locals
    if "self" in _locals:
        return _locals["self"].__class__
    return None


def get_frame_module_traceback(traceback=1) -> Union[types.ModuleType, None]:
    frame = get_frame_traceback(traceback + 1)
    module = inspect.getmodule(frame[0])
    return module


def get_frame_filepath_traceback(traceback=1):
    frame = get_frame_traceback(traceback + 1)
    return frame.filename


class TracedIdentity:
    def __init__(self, frame=None) -> None:
        self.frame = None
        self.func_name = None
        self.locals = None
        self.class_obj = None
        self.class_name = None
        self.module = None
        self.module_name = None
        self.filepath = None
        self.filename = None
        if frame:
            self.parse(frame)

    def parse(self, frame):
        self.frame = frame
        self.func_name = frame.function
        self.locals = frame[0].f_locals
        if "self" in self.locals:
            self.class_obj = self.locals["self"].__class__
            if self.class_obj:
                self.class_name = self.class_obj.__name__
        module: Union[types.ModuleType, None] = inspect.getmodule(frame[0])
        self.module = module
        self.module_name = module.__name__ if module else None
        self.filepath = path.abspath(frame.filename)
        self.filename = path.basename(frame.filename)
        return self

    def __str__(self) -> str:
        return (
            str(self.func_name)
            + ","
            + str(self.class_name)
            + ","
            + str(self.module_name)
            + ","
            + str(self.filepath)
            + ","
        )


def get_caller_identity_traceback(traceback=1):
    frame = get_frame_traceback(traceback + 1)
    traced_identity = TracedIdentity().parse(frame)
    return traced_identity
