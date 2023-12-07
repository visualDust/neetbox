# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# URL:    https://gong.host
# Date:   20230417

import collections
import time
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from functools import partial
from threading import Thread
from typing import Any, Callable, Optional, Union
from uuid import uuid4

from neetbox.config import get_module_level_config
from neetbox.core import Registry
from neetbox.logging import logger

__TIME_CTR_MAX_CYCLE = Decimal("99999.0")
__TIME_UNIT_SEC = Decimal("0.1")

_WATCH_QUERY_DICT = Registry("__pipeline_watch")
_LISTEN_QUERY_DICT = collections.defaultdict(lambda: {})
_UPDATE_VALUE_DICT = collections.defaultdict(lambda: {})

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%f"  # YYYY-MM-DDTHH:MM:SS.SSS

_DEFAULT_CHANNEL = str(
    uuid4()
)  # default watch and listen channel. users use this channel by default. default channel name varies on each start
SYSTEM_CHANNEL = "__system"  # values on this channel will upload via http client


@dataclass
class _WatchConfig(dict):
    name: str
    interval: Decimal
    initiative: bool
    channel: str = _DEFAULT_CHANNEL  # use channel to distinct those values to upload via http


class _WatchedFun:
    def __init__(self, func: Callable, cfg: _WatchConfig) -> None:
        self.func = func
        self.cfg = cfg

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)

    def __repr__(self) -> str:
        return f"{self.func.__name__}, {self.cfg}"


def __get(name: str, channel):
    _the_value = _UPDATE_VALUE_DICT[channel].get(name, default=None)
    if _the_value and "value" in _the_value:
        _the_value = _the_value["value"]
    return _the_value


def __update_and_get(name: str, *args, **kwargs):
    global _UPDATE_VALUE_DICT
    _watched_fun: _WatchedFun = _WATCH_QUERY_DICT[name]
    _watch_config = _watched_fun.cfg
    _channel = _watch_config.channel
    _the_value = _watched_fun(*args, **kwargs)
    _UPDATE_VALUE_DICT[_channel][name] = {
        "value": _the_value,
        "timestamp": datetime.now().strftime(DATETIME_FORMAT),
        "interval": None
        if _watch_config.interval is None
        else (_watch_config.interval * __TIME_UNIT_SEC),
    }

    def __call_listeners(_name: str, _value, _cfg: _WatchConfig):
        t0 = time.perf_counter()
        for _listener_name, _listener_func in _LISTEN_QUERY_DICT[_name].items():
            _listener_func(_value)
        t1 = time.perf_counter()
        delta_t = t1 - t0
        if _cfg.initiative:
            return
        _update_interval = _cfg.interval
        expected_time_limit = _update_interval * __TIME_UNIT_SEC
        if delta_t > expected_time_limit:
            logger.warn(
                f"Watched value {_name} takes longer time({delta_t:.8f}s) to update than it was expected    ({expected_time_limit}s)."
            )

    Thread(target=__call_listeners, args=(name, _the_value, _watch_config), daemon=True).start()

    return _the_value


def _watch(
    func: Callable,
    name: Optional[str],
    interval: float,
    initiative: bool = False,
    overwrite: bool = False,
    _channel: str = None,
):
    _channel = _channel or _DEFAULT_CHANNEL
    name = name or func.__name__
    _WATCH_QUERY_DICT._register(
        name=name,
        what=_WatchedFun(
            func=func,
            cfg=_WatchConfig(
                name,
                interval=None if interval is None else Decimal(str(interval)),
                initiative=initiative,
                channel=_channel,
            ),
        ),
        overwrite=overwrite,
        tags=_channel,
    )
    if initiative:  # initiatively update the value dict when the function was called manually
        logger.debug(
            f"added {name} to daemon monitor. It will update on each call of the function."
        )
        return partial(__update_and_get, name)
    else:
        _update_latency = Decimal(str(interval)) * __TIME_UNIT_SEC
        logger.debug(
            f"added {name} to daemon monitor. It will update every {_update_latency} second(s)."
        )
        return partial(__get, name, _channel)


def watch(
    name: str = None,
    interval: float = None,
    initiative: bool = True,
    overwrite: bool = False,
    _channel: str = None,
):
    # set interval to None if passively update
    interval = None if initiative else (interval or get_module_level_config()["updateInterval"])
    return partial(
        _watch,
        name=name,
        interval=interval,
        initiative=initiative,
        overwrite=overwrite,
        _channel=_channel,
    )


def _listen(
    func: Callable,  # the listener itself
    target: Union[str, Callable],  # user may pass a Callable or name to watch as target
    listener_name: Optional[str] = None,  # or user may pass a name to watch
    overwrite: bool = False,
):
    listener_name = listener_name or func.__name__
    if not isinstance(target, str):
        if type(target) is partial:  # solve target is a function with @watch
            if target.func in [__update_and_get, __get]:
                target = target.args[0]
        else:
            target = target.__name__

    if listener_name in _LISTEN_QUERY_DICT[target]:
        if not overwrite:
            logger.warn(
                f"There is already a listener called '{listener_name}' lisiting '{target}' If you want to overwrite, try to listen with 'overwrite=True'"
            )
            return func
        else:
            # logger.warn(
            #     f"There is already a listener called '{listener_name}' lisiting '{target}', overwriting."
            # )
            pass
    _LISTEN_QUERY_DICT[target][listener_name] = func
    logger.debug(f"{listener_name} is now lisiting to {target}.")
    return func


def listen(target: Union[str, Any], listener_name: Optional[str] = None, overwrite: bool = False):
    return partial(_listen, target=target, listener_name=listener_name, overwrite=overwrite)


def _update_thread():
    # update values
    _ctr = Decimal("0.0")
    while True:
        _ctr = (_ctr + __TIME_UNIT_SEC) % __TIME_CTR_MAX_CYCLE
        time.sleep(float(__TIME_UNIT_SEC))
        for _vname, _watched_fun in _WATCH_QUERY_DICT.items():
            _watch_config = _watched_fun.cfg
            if not _watch_config.initiative and _ctr % _watch_config.interval == Decimal(
                "0.0"
            ):  # do update
                _ = __update_and_get(_vname)


update_thread = Thread(target=_update_thread, daemon=True)
update_thread.start()
