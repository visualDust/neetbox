from time import time

from neetbox._protocol import *
from neetbox.utils.framing import get_frame_module_traceback

from ._client import connection


class Progress:
    def __init__(self, input, name=None):
        if isinstance(input, int):
            self.total = input
            self.iterator = iter(range(input))
        else:
            self.iterable = input
            self.iterator = iter(input)
            self.total = len(input)
        if name is None:
            name = get_frame_module_traceback().__name__
        self.name = name
        self.done = 0
        self.start_time = time()  # Track the start time

    def __enter__(self):
        # print(f"entering {self.name}")
        return self

    def __exit__(self, type, value, traceback):
        # print(f"leaving {self.name}")
        return

    def __iter__(self):
        return self

    def __next__(self):
        if self.done < self.total:
            self.done += 1
            elapsed_time = time() - self.start_time
            rate = (
                self.done / elapsed_time if elapsed_time > 0 else 0
            )  # Calculate the iteration rate
            connection.ws_send(
                event_type=EVENT_TYPE_NAME_PROGRESS,
                series=self.name,
                payload={"done": self.done, "total": self.total, "rate": rate},
                _history_len=1,
            )
            print(f"{self.done}/{self.total}, {rate}/sec")
            return next(self.iterator)
        else:
            raise StopIteration

    def __len__(self):
        return self.total


# if __name__ == "__main__":
#     from tqdm import tqdm
#     from time import sleep

#     with Progress(10) as p:
#         for i in p:
#             sleep(0.1)  # Simulate some work

#     with tqdm(Progress(range(10))) as p:
#         for i in p:
#             sleep(0.1)  # Simulate some work
