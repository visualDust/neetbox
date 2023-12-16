# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231217

from time import time
from typing import Callable

from ._client import connection

from neetbox._protocol import *
from neetbox.utils.framing import get_caller_identity_traceback


class Progress:
    def __init__(self, input):
        if isinstance(input, int):
            self.total = input
            self.iterator = iter(range(input))
        else:
            self.iterable = input
            self.iterator = iter(input)
            self.total = len(input)
        self.caller_identity = get_caller_identity_traceback(traceback=2)
        self.done = 0
        self.start_time = time()  # Track the start time
        self.timestamp = get_timestamp()

    def __enter__(self):
        # print(f"entering {self.caller_identity}")
        return self

    def __exit__(self, type, value, traceback):
        # print(f"leaving {self.caller_identity}")
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
            iter_next = next(self.iterator)
            current_name = f"{iter_next.__name__ if isinstance(iter_next, Callable) else iter_next}"
            connection.ws_send(
                event_type=EVENT_TYPE_NAME_PROGRESS,
                series=self.caller_identity.last_traceable,
                payload={
                    "step": self.done,
                    "current": current_name,
                    "total": self.total,
                    "rate": rate,
                },
                timestamp=self.timestamp,
                _history_len=1,
            )
            return iter_next
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
