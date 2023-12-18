# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231217

from time import time
from ._client import connection
from neetbox._protocol import *
from neetbox.utils.framing import get_caller_identity_traceback
from neetbox.utils.massive import describe_object


class Progress:
    total: int
    done: int
    iterator: enumerate
    timestamp: str

    def __init__(self, input):
        if isinstance(input, int):
            self.total = input
            self.iterator = iter(range(input))
        elif isinstance(input, enumerate):
            self.total = None
            self.iterator = input
        else:
            self.total = len(input)
            self.iterator = iter(input)
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
        if self.total and self.done > self.total:
            raise StopIteration
        self.done += 1
        elapsed_time = time() - self.start_time
        rate = self.done / elapsed_time if elapsed_time > 0 else 0  # Calculate the iteration rate
        iter_next = next(self.iterator)

        connection.ws_send(
            event_type=EVENT_TYPE_NAME_PROGRESS,
            series=self.caller_identity.last_traceable,
            payload={
                "step": self.done,
                "current": describe_object(iter_next, length_limit=16),
                "total": self.total,
                "rate": rate,
            },
            timestamp=self.timestamp,
            _history_len=1,
        )
        return iter_next

    def __len__(self):
        if self.total is None:
            raise RuntimeError("you are trying to get length of an enumerate object")
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
