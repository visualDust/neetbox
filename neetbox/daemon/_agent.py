import functools
import inspect
from typing import Callable, Optional
from ast import literal_eval
from neetbox.core import Registry
from neetbox.utils.mvc import Singleton
from neetbox.logging import logger


class PackedAction(Callable):
    def __init__(self, function: Callable, name=None, **kwargs):
        super().__init__(**kwargs)
        self.function = function
        self.name = name if name else function.__name__
        self.argspec = inspect.getfullargspec(self.function)

    def __call__(self, **argv):
        self.function(argv)

    def eval_call(self, params: dict):
        eval_params = dict((k, literal_eval(v)) for k, v in params.items())
        return self.function(**eval_params)


class _NeetAction(metaclass=Singleton):
    __ACTION_POOL: Registry = Registry("__NEET_ACTIONS")

    def register(
        self,
        *,
        name: Optional[str] = None,
    ):
        return functools.partial(self._register, name=name)

    def _register(self, function: Callable, name: str = None):
        packed = PackedAction(function=function, name=name)
        _NeetAction.__ACTION_POOL._register(what=packed, name=packed.name, force=True)
        return function

    def get_actions(self):
        action_names = _NeetAction.__ACTION_POOL.keys()
        actions = {}
        for n in action_names:
            actions[n] = _NeetAction.__ACTION_POOL[n].argspec
        return actions

    def eval_call(self, name: str, params: dict):
        if name not in _NeetAction.__ACTION_POOL:
            logger.err(f"Could not find action with name {name}, action stopped.")
            return False
        return _NeetAction.__ACTION_POOL[name].eval_call(params)


# singleton
neet_action = _NeetAction()


# example
if __name__ == "__main__":

    @neet_action.register(name="some")
    def some(a, b):
        print(a, b)

    print('registered actions:')
    print(neet_action.get_actions())

    print("calling 'some")
    neet_action.eval_call("some", {"a": "3", "b": "4"})
