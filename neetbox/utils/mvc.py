# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20230416


def singleton(class_):
    class class_w(class_):
        _instance = None

        def __new__(cls, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w, cls).__new__(cls, *args, **kwargs)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def patch(func=None, *, name=None, overwrite=True):
    """Patch a function into a class type

    Args:
        func (Function): A function that takes at least one argument with a specific class type 'self:YourClass'
        name (str, optional): The name to assign to the method in the class. Defaults to the function's name.
        overwrite (bool, optional): Whether to overwrite an existing method in the class. Defaults to True.

    Returns:
        function: The patched function
    """
    if func is None:
        return lambda f: patch(f, name=name, overwrite=overwrite)

    # Extract the class from the first parameter's type annotation
    cls = next(iter(func.__annotations__.values()))
    method_name = name or func.__name__

    # Check if the method already exists in the class
    if not overwrite and hasattr(cls, method_name):
        # Do not overwrite; return the original function unmodified
        return func

    # Update function metadata
    func.__qualname__ = f"{cls.__name__}.{method_name}"
    func.__module__ = cls.__module__

    # Patch the function into the class
    setattr(cls, method_name, func)
    return func
