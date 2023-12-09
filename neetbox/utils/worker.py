import time
from concurrent.futures import ThreadPoolExecutor
from typing import Callable

MAX_WORKERS = 4


class AsyncWoker:
    EXECUTOR = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def __init__(self, func: Callable):
        self.func = func

    def __call__(self, *args, **kwargs):
        return AsyncWoker.EXECUTOR.submit(self.func, *args, **kwargs)  # type: ignore


if __name__ == "__main__":

    @AsyncWoker
    def add_image(image, a=1, b=2):
        time.sleep(image)
        print("b")
        print(a, b)
        return 5

    for i in range(10):
        print(f"i: {i}")
        add_image(i)
        add_image(i, a=2, b=2)
