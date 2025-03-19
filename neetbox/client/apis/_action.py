# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231122

import functools
import inspect
from ast import literal_eval
from threading import Thread
from typing import Callable, Optional

from vdtoys.mvc import Singleton
from vdtoys.registry import Registry

from neetbox._protocol import *
from neetbox.logging import logger

from .._client import connection


class Action(Callable):
    def __init__(
        self,
        function: Callable,
        name: str = None,
        description: str = None,
        blocking: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.function = function
        self.name = name if name else function.__name__
        self.description = description
        self.argspec = inspect.getfullargspec(self.function)
        self.blocking = blocking

    def get_props_dict(self):
        # _arg_dict = {
        #     _arg_name: self.argspec.annotations.get(_arg_name, None)
        #     for _arg_name in self.argspec.args
        # }
        _arg_anno_dict = self.function.__annotations__
        _args = self.argspec.args
        _arg_dict = {}
        for _arg_name in _args:
            _arg_type = _arg_anno_dict.get(_arg_name, any)
            _arg_dict[_arg_name] = _arg_type if isinstance(_arg_type, str) else _arg_type.__name__
        return {
            "description": self.description,
            "args": _arg_dict,
            "blocking": self.blocking,
        }

    def __call__(self, **argv):
        self.function(argv)  # ignore blocking

    def eval_call(self, params: dict):
        eval_params = {}
        for k, v in params.items():
            if v:
                eval_params[k] = literal_eval(v)
        return self.function(**eval_params)


class ActionManager(metaclass=Singleton):
    ACTION_POOL: Registry = Registry("__NEET_ACTIONS")
    _is_initialized = False

    def get_action_dict(self):
        return {name: self.ACTION_POOL[name].get_props_dict() for name in self.ACTION_POOL.keys()}

    def eval_call(self, name: str, params: dict, callback: Optional[Callable] = None):
        if name not in self.ACTION_POOL:
            logger.err(f"Could not find action with name {name}, action stopped.")
            return False
        target_action: Action = self.ACTION_POOL[name]
        logger.log(
            f"Agent runs function '{target_action.name}', blocking = {target_action.blocking}"
        )

        def run_and_callback():
            try:
                returned_data = target_action.eval_call(params)
            except Exception as e:
                returned_data = e
                logger.warn(f"action {target_action} failed with exception {e}")
            if callback:
                callback(returned_data)

        if not target_action.blocking:  # non-blocking run in thread
            Thread(
                target=run_and_callback,
                daemon=True,
            ).start()
            return
        else:  # blocking run
            run_and_callback()
            return

    def _initialize(self):
        if not self._is_initialized:

            @connection.ws_subscribe(event_type_name=EVENT_TYPE_NAME_ACTION)
            def _listen_to_actions(message: EventMsg):
                actionManager.eval_call(
                    name=message.payload[NAME_KEY],
                    params=message.payload[ARGS_KEY],
                    callback=lambda x: connection.ws_send(
                        event_type=EVENT_TYPE_NAME_ACTION,
                        payload={
                            NAME_KEY: message.payload[NAME_KEY],
                            (ERROR_KEY if isinstance(x, Exception) else RESULT_KEY): x,
                        },
                        event_id=message.event_id,
                    ),
                )

            self._is_initialized = True

    def register(self, name: Optional[str] = None, description: str = None, blocking: bool = False):
        """register function as action visiable on frontend page

        Args:
            name (Optional[str], optional): name of the action. Defaults to None(neetbox will use the function name when set to None).
            description (str, optional): description of the action. Defaults to None(neetbox will use function docs as default when set to None).
            blocking (bool, optional): whether to run the action in a blocked query. Defaults to False.

        Returns:
            Callable: the function itself.
        """
        if not self._is_initialized:
            self._initialize()
        return functools.partial(
            self._register, name=name, description=description, blocking=blocking
        )

    def _register(
        self, function: Callable, name: str = None, description: str = None, blocking: bool = False
    ):
        if (
            description is None and function.__doc__ is not None
        ):  # parse function doc as description
            description = function.__doc__
            if description:
                _description_lines = []
                for _line in description.split("\n"):
                    if len(_line):  # remove empty lines
                        _description_lines.append(_line)
                # find shortest lstrip
                min_lstrip = 99999
                for _line in _description_lines[1:]:  # skip first line
                    min_lstrip = min(len(_line) - len(_line.lstrip()), min_lstrip)
                _parsed_description = _description_lines[0] + "\n"
                for _line in _description_lines[1:]:
                    _parsed_description += _line[min_lstrip:] + "\n"
                description = _parsed_description

        packed = Action(function=function, name=name, description=description, blocking=blocking)
        self.ACTION_POOL._register(what=packed, name=packed.name, overwrite=True)
        connection.ws_send(
            event_type=EVENT_TYPE_NAME_STATUS,
            series="action",
            payload=self.get_action_dict(),
        )
        return function


actionManager = ActionManager()
