import asyncio
import functools
import json
from collections import defaultdict
from dataclasses import dataclass
from typing import Callable, Dict

from rich.console import Console
from vdtoys.framing import TracebackInfo, get_caller_info_traceback
from vdtoys.mvc import Singleton

console = Console()
MessageType = str
NameType = str


@dataclass
class MessageListener:
    creator: TracebackInfo
    message_type: str
    name: str
    func: Callable

    @property
    def json(self):
        return {
            "creator": self.creator.json,
            "messageType": self.message_type,
            "listenerName": self.name,
            "function": self.func.__name__,
        }


class Messaging(metaclass=Singleton):
    _listener_dicts: Dict[MessageType, Dict[NameType, MessageListener]] = defaultdict(dict)

    def listener(self, message_type: str, name: str = None):
        caller = get_caller_info_traceback(stack_offset=2)

        def _listener(func: Callable, message_type: str, name: str):
            if asyncio.iscoroutinefunction(func):
                raise RuntimeError(
                    f"cannot add listener func {func}, messaging does not support async listeners."
                )
            name = name or f"{caller.strid}:{func.__name__}"
            if name in self._listener_dicts[message_type]:
                raise RuntimeError(
                    f"message listener for message type {message_type} with name {name} already exist"
                )
            self._listener_dicts[message_type][name] = MessageListener(
                creator=caller, message_type=message_type, name=name, func=func
            )
            return func

        return functools.partial(_listener, message_type=message_type, name=name)

    def send(self, message_type: str, message: any = None):
        if message_type in self._listener_dicts:
            listener: MessageListener
            for _, listener in self._listener_dicts[message_type].items():
                listener.func(message)

    @property
    def json(self):
        return json.dumps(self._listener_dicts, default=str)


messaging = Messaging()  # singleton
