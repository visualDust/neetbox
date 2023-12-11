import functools
import inspect
from ast import literal_eval
from threading import Thread
from typing import Callable, Optional

from neetbox._daemon._protocol import *
from neetbox._daemon.client._client import connection
from neetbox.core import Registry
from neetbox.logging import logger
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
        target_action: PackedAction = _NeetActionManager.__ACTION_POOL[name]
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

    def register(name: Optional[str] = None, description: str = None, blocking: bool = False):
        """register function as action visiable on frontend page

        Args:
            name (Optional[str], optional): name of the action. Defaults to None(neetbox will use the function name when set to None).
            description (str, optional): description of the action. Defaults to None(neetbox will use function docs as default when set to None).
            blocking (bool, optional): whether to run the action in a blocked query. Defaults to False.

        Returns:
            Callable: the function itself.
        """
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
        connection.ws_send(
            event_type=EVENT_TYPE_NAME_STATUS,
            series="action",
            payload=_NeetActionManager.get_action_dict(),
        )
        return function


@connection.ws_subscribe(event_type_name=EVENT_TYPE_NAME_ACTION)
def _listen_to_actions(message: EventMsg):
    _NeetActionManager.eval_call(
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
