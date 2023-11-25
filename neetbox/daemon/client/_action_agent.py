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
    def __init__(self, function: Callable, name=None, blocking=False, **kwargs):
        super().__init__(**kwargs)
        self.function = function
        self.name = name if name else function.__name__
        self.argspec = inspect.getfullargspec(self.function)
        self.blocking = blocking

    def __call__(self, **argv):
        self.function(argv)  # ignore blocking

    def eval_call(self, params: dict):
        eval_params = dict((k, literal_eval(v)) for k, v in params.items())
        return self.function(**eval_params)


class _NeetActionManager(metaclass=Singleton):
    __ACTION_POOL: Registry = Registry("__NEET_ACTIONS")

    def get_action_names():
        action_names = _NeetActionManager.__ACTION_POOL.keys()
        actions = {}
        for n in action_names:
            actions[n] = _NeetActionManager.__ACTION_POOL[n].argspec
        return actions

    def get_action_dict():
        action_dict = {}
        action_names = _NeetActionManager.__ACTION_POOL.keys()
        for name in action_names:
            action = _NeetActionManager.__ACTION_POOL[name]
            action_dict[name] = {"args": action.argspec.args, "blocking": action.blocking}
        return action_dict

    def eval_call(name: str, params: dict, callback: None):
        if name not in _NeetActionManager.__ACTION_POOL:
            logger.err(f"Could not find action with name {name}, action stopped.")
            return False
        target_action = _NeetActionManager.__ACTION_POOL[name]
        logger.log(
            f"Agent runs function '{target_action.name}', blocking = {target_action.blocking}"
        )
        if not target_action.blocking:  # non-blocking run in thread

            def run_and_callback(target_action, params, callback):
                returned_data = target_action.eval_call(params)
                if callback:
                    callback(returned_data)

            Thread(
                target=run_and_callback,
                kwargs={"target_action": target_action, "params": params, "callback": callback},
                daemon=True,
            ).start()
            return None
        else:  # blocking run
            return target_action.eval_call(params)

    @watch(name="__action", initiative=True, _channel=SYSTEM_CHANNEL)
    def _update_action_dict():
        # for status updater
        return _NeetActionManager.get_action_dict()

    def register(name: Optional[str] = None, blocking: bool = False):
        return functools.partial(_NeetActionManager._register, name=name, blocking=blocking)

    def _register(function: Callable, name: str = None, blocking: bool = False):
        packed = PackedAction(function=function, name=name, blocking=blocking)
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
            event_type="action", payload={"name": _action_name, "result": x}, _event_id=_event_id
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
