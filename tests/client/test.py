import os
from random import random
from time import sleep

from neetbox.daemon import action
from neetbox.integrations.environment import hardware, platform
from neetbox.logging import logger
from neetbox.pipeline import listen, watch


@watch("train", initiative=True)
def train(epoch):
    loss, acc = random(), random()
    return {"loss": loss, "acc": acc}


@listen("train")
def print_to_console(metrix):
    logger.log(f"metrix from train: {metrix}")


@watch("log-some-prefix", interval=50)
def log_with_some_prefix():
    logger.ok("some ok")
    logger.info("some info")
    logger.debug("some debug")
    logger.warn("some warn")
    logger.err("some error")


@watch(freq=40)
def log_with_some_prefix_1():
    logger.ok("some ok")


@watch(freq=50)
def log_with_some_prefix_2():
    logger.ok("some ok")


@watch(freq=60)
def log_with_some_prefix_200():
    logger.ok("some ok")


@watch(freq=88)
def log_with_some_prefix_333():
    logger.ok("some ok")


@watch(freq=30)
def log_with_some_prefix_500():
    logger.ok("some ok")


@action(name="action-1")
def action_1(text: str):
    """take action 1

    Args:
        text (str): text to print
    """
    logger.log(f"action 1 triggered. text = {text}")


@action(name="action-2")
def action_2(text1, text2):
    logger.log(f"action 2 triggered. text1 = {text1}, text2 = {text2}")


@action(name="wait-for-sec", blocking=True)
def action_2(sec):
    sec = int(sec)
    logger.log(f"wait for {sec} sec.")


@action(name="shutdown", blocking=True)
def sys_exit():
    logger.log("shutdown received, shutting down immediately.")
    os._exit(0)


for i in range(99999):
    sleep(1)
    train(i)
