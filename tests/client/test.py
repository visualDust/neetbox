import os
import time
from random import random
from time import sleep

import snake

from neetbox.daemon import action
from neetbox.frontend import impost
from neetbox.logging import logger
from neetbox.pipeline import listen, watch


@watch("train", initiative=True)
def train(epoch):
    loss, acc = random(), random()
    return {"loss": loss, "acc": acc}


@listen("train")
def print_to_console(metrix):
    logger.log(f"metrix from train: {metrix}")


@watch("log-some-prefix", initiative=False, interval=5.0)
def log_with_some_prefix():
    logger.ok("some ok")
    logger.info("some info")
    logger.debug("some debug")
    logger.warn("some warn")
    logger.err("some error")


@action()
def log_perf_test(interval: int, count: int):
    for i in range(count):
        sleep(interval)
        logger.info(f"log_perf_test {i + 1}/{count}")


@action(name="action-1")
def action_1(text: str):
    """take action 1

    Args:
        text (string): print this string to console as log
    """

    logger.log(f"action 1 triggered. text = {text}")


@action()
def action_bool(enable: bool):
    logger.info(f"action_bool triggered. enable = {enable}")
    return {"enable": enable}


@action()
def action_very_long_name(arg_with_very_long_long_name: int):
    return {"very_long_long_result_key": arg_with_very_long_long_name}


def def_plus_1(val):
    @action(name="plus1", description=f"val={val}")
    def plus_1():
        def_plus_1(val + 1)


def_plus_1(0)


@action(name="action-2")
def action_2(text1, text2):
    logger.log(f"action 2 triggered. text1 = {text1}, text2 = {text2}")


@action(name="wait-for-sec", blocking=False)
def wait_for_sec(sec):
    sec = int(sec)
    logger.log(f"wait for {sec} sec.")
    time.sleep(sec)


@action(name="block-for-sec", blocking=True)
def block_for_sec(sec):
    sec = int(sec)
    logger.log(f"block for {sec} sec.")
    time.sleep(sec)


@action(name="eval")
def eval_code(code: str):
    logger.log(f"running code {code}")
    logger.info("eval result: ", eval(code))


_id_indexer = 0


@action()
def new_action(id: int):
    global _id_indexer

    @action(name=f"new_action_{_id_indexer}")
    def action_():
        pass

    _id_indexer += 1


@action(name="shutdown", description="shutdown your process", blocking=True)
def sys_exit():
    logger.log("shutdown received, shutting down immediately.")
    os._exit(0)


@action()
def send_image():
    from PIL import Image

    with Image.open("logo.png") as logo_image:
        impost(logo_image, name="logo")


for i in range(99999):
    sleep(1)
    train(i)
