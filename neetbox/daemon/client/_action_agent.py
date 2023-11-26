import functools
import inspect
from ast import literal_eval
from threading import Thread
from typing import Callable, Optional

from neetbox.core import Registry
from neetbox.daemon._protocol import *
from neetbox.daemon.client._client import connection
from neetbox.logging import logger
from neetbox.pipeline import watch
from neetbox.pipeline._signal_and_slot import SYSTEM_CHANNEL
from neetbox.utils.mvc import Singleton

class PackedAction(Callable):
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
        __arg_dict = {_arg_name: _arg_anno_dict.get(_arg_name, any).__name__ for _arg_name in _args}
        return {
            "description": self.description,
            "args": __arg_dict,
            "blocking": self.blocking,
        }

    def __call__(self, **argv):
        self.function(argv)  # ignore blocking

    def eval_call(self, params: dict):
        eval_params = dict((k, literal_eval(v)) for k, v in params.items())
        return self.function(**eval_params)


class _NeetActionManager(metaclass=Singleton):
    __ACTION_POOL: Registry = Registry("__NEET_ACTIONS")

    @staticmethod
    def get_action_names():
        return {
            n: _NeetActionManager.__ACTION_POOL[n].argspec
            for n in _NeetActionManager.__ACTION_POOL.keys()
        }

    @staticmethod
    def get_action_dict():
        return {
            name: _NeetActionManager.__ACTION_POOL[name].get_props_dict()
            for name in _NeetActionManager.__ACTION_POOL.keys()
        }

    @staticmethod
    def eval_call(name: str, params: dict, callback: Optional[Callable] = None):
        if name not in _NeetActionManager.__ACTION_POOL:
            logger.err(f"Could not find action with name {name}, action stopped.")
            return False
        target_action = _NeetActionManager.__ACTION_POOL[name]
        logger.log(
            f"Agent runs function '{target_action.name}', blocking = {target_action.blocking}"
        )

        def run_and_callback():
            try:
                returned_data = target_action.eval_call(params)
            except Exception as e:
                returned_data = e
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

    @watch(name="__action", initiative=True, _channel=SYSTEM_CHANNEL)
    def _update_action_dict():
        # for status updater
        return _NeetActionManager.get_action_dict()

    def register(name: Optional[str] = None, description: str = None, blocking: bool = False):
        return functools.partial(
            _NeetActionManager._register, name=name, description=description, blocking=blocking
        )

    def _register(
        function: Callable, name: str = None, description: str = None, blocking: bool = False
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

        packed = PackedAction(
            function=function, name=name, description=description, blocking=blocking
        )
        _NeetActionManager.__ACTION_POOL._register(what=packed, name=packed.name, overwrite=True)
        _NeetActionManager._update_action_dict()  # update for sync
        return function


@connection.ws_subscribe(event_type_name="action")
def __listen_to_actions(msg):
    _payload = msg[PAYLOAD_NAME_KEY]
    _event_id = msg[EVENT_ID_NAME_KEY]
    _action_name = _payload["name"]
    _action_args = _payload["args"]
    _NeetActionManager.eval_call(
        name=_action_name,
        params=_action_args,
        callback=lambda x: connection.ws_send(
            event_type="action",
            payload={"name": _action_name, ("error" if isinstance(x, Exception) else "result"): x},
            event_id=_event_id,
        ),
    )


# example
if __name__ == "__main__":
    import time

    @_NeetActionManager.register(name="some")
    def some(a, b):
        time.sleep(1)
        return f"a = {a}, b = {b}"

    print("registered actions:")
    action_dict = _NeetActionManager.get_action_dict()
    print(action_dict)

    def callback_fun(text):
        print(f"callback_fun print: {text}")

    _NeetActionManager.eval_call(name="some", params={"a": "3", "b": "4"}, callback=callback_fun)
    print("you should see this line first before callback_fun print")
    time.sleep(4)
