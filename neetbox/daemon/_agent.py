import functools
import inspect
from threading import Thread
from typing import Callable, Optional
from ast import literal_eval
from neetbox.core import Registry
from neetbox.utils.mvc import Singleton
from neetbox.logging import logger


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


class _NeetAction(metaclass=Singleton):
    __ACTION_POOL: Registry = Registry("__NEET_ACTIONS")

    def register(self, *, name: Optional[str] = None, blocking: bool = False):
        return functools.partial(self._register, name=name, blocking=blocking)

    def _register(self, function: Callable, name: str = None, blocking: bool = False):
        packed = PackedAction(function=function, name=name, blocking=blocking)
        _NeetAction.__ACTION_POOL._register(what=packed, name=packed.name, force=True)
        return function

    def get_actions(self):
        action_names = _NeetAction.__ACTION_POOL.keys()
        actions = {}
        for n in action_names:
            actions[n] = _NeetAction.__ACTION_POOL[n].argspec
        return actions

    def eval_call(self, name: str, params: dict, callback: None):
        if name not in _NeetAction.__ACTION_POOL:
            logger.err(f"Could not find action with name {name}, action stopped.")
            return False
        target_action = _NeetAction.__ACTION_POOL[name]
        logger.log(f"Agent runs function '{target_action.name}', blocking = {target_action.blocking}")
        if not target_action.blocking:  # non-blocking run in thread

            def run_and_callback(target_action, params, callback):
                returned_data = target_action.eval_call(params)
                if callback:
                    callback(returned_data)

            Thread(
                target=run_and_callback,
                kwargs={"target_action": target_action, "params": params, "callback": callback},
            ).start()
            return None
        else:  # blocking run
            return target_action.eval_call(params)


# singleton
neet_action = _NeetAction()


# example
if __name__ == "__main__":
    import time

    action = neet_action

    @action.register(name="some")
    def some(a, b):
        time.sleep(1)
        return f"a = {a}, b = {b}"

    print("registered actions:")
    print(neet_action.get_actions())

    def callback_fun(text):
        print(f"callback_fun print: {text}")

    neet_action.eval_call("some", {"a": "3", "b": "4"}, callback=callback_fun)
    print("you should see this line first before callback_fun print")
    time.sleep(4)
