import functools
import os
import time
from concurrent.futures import ThreadPoolExecutor

_ThreadPoolExecutor = ThreadPoolExecutor()


def nonblocking(func):
    @functools.wraps(func)
    def _use_thread_pool(*args, **kwargs):
        try:
            return _ThreadPoolExecutor.submit(func, *args, **kwargs)  # type: ignore
        except Exception as e:
            raise e

    return _use_thread_pool


def update_dict_recursively(self: dict, the_other: dict):
    for _k, _v in the_other.items():
        if type(_v) is dict:  # currently resolving a dict child
            if _k in self:  # dfs merge
                update_dict_recursively(self=self[_k], the_other=the_other[_k])
            else:
                self[_k] = the_other[_k]
        else:  # not a dict, overwriting
            self[_k] = the_other[_k]


def get_user_config_directory():
    """Returns a platform-specific root directory for user config settings."""
    # On Windows, prefer %LOCALAPPDATA%, then %APPDATA%, since we can expect the
    # AppData directories to be ACLed to be visible only to the user and admin
    # users (https://stackoverflow.com/a/7617601/1179226). If neither is set,
    # return None instead of falling back to something that may be world-readable.
    if os.name == "nt":
        appdata = os.getenv("LOCALAPPDATA")
        if appdata:
            return appdata
        appdata = os.getenv("APPDATA")
        if appdata:
            return appdata
        return None
    # On non-windows, use XDG_CONFIG_HOME if set, else default to ~/.config.
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    if xdg_config_home:
        return xdg_config_home
    return os.path.join(os.path.expanduser("~"), ".config")


def check_read_toml(path) -> bool:
    import toml

    if not os.path.isfile(path):  # but config file not exist
        return False
    try:
        return toml.load(path)  # try load as toml
    except Exception as e:
        return False


if __name__ == "__main__":

    @nonblocking
    def add_image(image, a=1, b=2):
        time.sleep(image)
        print("b")
        print(a, b)
        return 5

    for i in range(10):
        print(f"i: {i}")
        add_image(i)
        add_image(i, a=2, b=2)
