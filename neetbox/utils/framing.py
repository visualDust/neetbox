# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230319

from dataclasses import dataclass
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


@dataclass
class TracebackIdentity:
    frame = None
    func_name = None
    locals = None
    class_obj = None
    class_name = None
    module = None
    module_name = None
    filepath = None
    filename = None

    @classmethod
    def parse(cls, frame) -> "TracebackIdentity":
        instance = TracebackIdentity()
        instance.frame = frame
        instance.func_name = frame.function if frame.function != "<module>" else None
        instance.locals = frame[0].f_locals
        if "self" in instance.locals:
            instance.class_obj = instance.locals["self"].__class__
            if instance.class_obj:
                instance.class_name = instance.class_obj.__name__
        module: Union[types.ModuleType, None] = inspect.getmodule(frame[0])
        instance.module = module
        instance.module_name = module.__name__ if module else None
        instance.filepath = path.abspath(frame.filename)
        instance.filename = path.basename(frame.filename)
        return instance

    @property
    def last_traceable(self):
        for identity in [self.func_name, self.class_name, self.module_name, self.filepath, None]:
            if identity is not None:
                return identity

    @property
    def json(self):
        return {
            "file": f"{self.filepath}",
            "modlue": f"{self.module_name}",
            "class": f"{self.class_name}",
            "function": f"{self.func_name}",
        }

    @property
    def sequence(self):
        return [
            prop
            for prop in [self.filepath, self.module_name, self.class_name, self.func_name]
            if prop is not None
        ]

    def __eq__(self, __value: object) -> bool:
        assert isinstance(
            __value, TracebackIdentity
        ), f"cannot compare {__value} as a {TracebackIdentity}"
        return (
            self.filepath == __value.filepath
            and self.module_name == __value.module_name
            and self.class_name == __value.class_name
            and self.func_name == __value.func_name
        )

    def __repr__(self) -> str:
        return "\n".join([f"{k}:\t\t{v}" for k, v in self.json.items()])


def get_caller_identity_traceback(traceback=1):
    frame = get_frame_traceback(traceback + 1)
    return TracebackIdentity.parse(frame)
