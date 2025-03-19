# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20231217

from time import time
from uuid import uuid4

from vdtoys.framing import get_caller_info_traceback

from neetbox._protocol import *
from neetbox.utils.massive import describe_object

from .._client import connection


class Progress:
    total: int
    done: int
    iterator: enumerate
    timestamp: str

    def __init__(self, input: Union[int, enumerate, any], *, name=None):
        """Decorate an iterable object, returning an iterator. Neetbox will send progress to frontend while you are iterating through it.

        Args:
            input (Union[int, enumerate, any]): Something to iterate or something to create enumeratable object.
        """
        self.name = name
        if isinstance(input, int):
            self.total = input
            self.iterator = iter(range(input))
        elif isinstance(input, enumerate):
            self.total = None
            self.iterator = input
        else:
            self.total = len(input)
            self.iterator = iter(input)
        self.caller_identity = get_caller_info_traceback(stack_offset=2)

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

    @classmethod
    def _update(
        cls,
        *,
        name: str,
        what_is_current: any,
        done: int,
        total: int,
        rate: float,
        timestamp=None,
    ):
        connection.ws_send(
            event_type=EVENT_TYPE_NAME_PROGRESS,
            series=name,
            payload={
                NAME_KEY: name,
                "step": done,
                "current": what_is_current,
                "total": total,
                "rate": rate,
            },
            timestamp=timestamp or get_timestamp(),
            _history_len=1,
        )

    def __next__(self):
        if self.total and self.done > self.total:
            raise StopIteration
        self.done += 1
        elapsed_time = time() - self.start_time
        rate = self.done / elapsed_time if elapsed_time > 0 else 0  # Calculate the iteration rate
        iter_next = next(self.iterator)

        self.__class__._update(
            name=self.caller_identity.strid + (self.name or ""),
            done=self.done,
            what_is_current=describe_object(iter_next, length_limit=16),
            total=self.total,
            rate=rate if self.done > 1 else -1.0,
            timestamp=self.timestamp,
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
