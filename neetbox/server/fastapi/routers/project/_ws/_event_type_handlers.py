# -*- coding: utf-8 -*-
#
# Author: GavinGong aka VisualDust
# Github: github.com/visualDust
# Date:   20240110

from collections import defaultdict
from typing import Callable

from neetbox._protocol import *

from .._bridge import Bridge

EVENT_TYPE_HANDLERS = defaultdict(list)


def on_event(type_name: str, *args):
    def _on_event(func: Callable) -> Callable:
        EVENT_TYPE_HANDLERS[type_name].append(func)
        return func

    return _on_event


async def on_event_type_default_json(
    message: EventMsg,
    forward_to: IdentityType = IdentityType.OTHERS,
    save_history=True,
):
    bridge = Bridge.of_id(message.project_id)
    if save_history:
        message.id = bridge.save_json_to_history(
            table_name=message.event_type,
            json_data=message.payload,
            series=message.series,
            run_id=message.run_id,
            timestamp=message.timestamp,
            num_row_limit=message.history_len,
        )
    if forward_to:
        if forward_to == IdentityType.SELF:
            forward_to = message.identity_type
        if forward_to == IdentityType.OTHERS:
            forward_to = (
                IdentityType.WEB if message.identity_type == IdentityType.CLI else IdentityType.CLI
            )
        if forward_to in [IdentityType.WEB, IdentityType.BOTH]:
            await bridge.ws_send_to_frontends(message)  # forward to frontends
        elif forward_to in [IdentityType.CLI, IdentityType.BOTH]:
            await bridge.ws_send_to_client(message, run_id=message.run_id)  # forward to frontends

    return  # return after handling log forwardin


@on_event(EVENT_TYPE_NAME_STATUS)
async def on_event_type_status(message: EventMsg):
    bridge = Bridge.of_id(message.project_id)
    bridge.set_status(run_id=message.run_id, series=message.series, value=message.payload)


@on_event(EVENT_TYPE_NAME_HPARAMS)
async def on_event_type_hyperparams(message: EventMsg):
    bridge = Bridge.of_id(message.project_id)
    current_hyperparams = bridge.get_status(
        run_id=message.run_id, series=EVENT_TYPE_NAME_HPARAMS
    )  # get hyper params from status
    if message.series:  # if series of hyperparams specified
        current_hyperparams[message.series] = message.payload
    else:
        for k, v in message.payload.items():
            current_hyperparams[k] = v
    bridge.set_status(
        run_id=message.run_id, series=EVENT_TYPE_NAME_HPARAMS, value=current_hyperparams
    )


@on_event(EVENT_TYPE_NAME_ACTION)
async def on_event_type_action(message: EventMsg):
    await on_event_type_default_json(
        message=message, forward_to=IdentityType.OTHERS, save_history=False
    )
