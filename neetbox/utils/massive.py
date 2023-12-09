import functools
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
