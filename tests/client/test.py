import math
import os
import time
from random import random
from time import sleep

import neetbox
from neetbox import logger


@neetbox.watch("train", initiative=True)
def train(epoch):
    loss, acc = random(), random()
    neetbox.add_scalar("sin", epoch, math.sin(epoch * 0.1))
    neetbox.add_scalar("cos", epoch, math.cos(epoch * 0.1))
    return {"loss": loss, "acc": acc}


@neetbox.listen("train")
def print_to_console(metrix):
    logger.log(f"metrix from train: {metrix}")


@neetbox.watch("log-some-prefix", initiative=False, interval=5.0)
def log_with_some_prefix():
    logger.ok("some ok")
    logger.info("some info")
    logger.debug("some debug")
    logger.warn("some warn")
    logger.err("some error")


@neetbox.action()
def scalar_perf_test(interval: float, count: int):
    for i in range(count):
        sleep(interval)
        neetbox.add_scalar("scalar_perf_test", i, math.cos(i * 0.1))


@neetbox.action()
def log_perf_test(interval: int, count: int):
    for i in range(count):
        sleep(interval)
        logger.info(f"log_perf_test {i + 1}/{count}")


@neetbox.action(name="action-1")
def action_1(text: str):
    """take action 1

    Args:
        text (string): print this string to console as log
    """

    logger.log(f"action 1 triggered. text = {text}")


@neetbox.action()
def action_bool(enable: bool):
    logger.info(f"action_bool triggered. enable = {enable}")
    return {"enable": enable}


@neetbox.action()
def action_very_long_name(arg_with_very_long_long_name: int):
    return {"very_long_long_result_key": arg_with_very_long_long_name}


def def_plus_1(val):
    @neetbox.action(name="plus1", description=f"val={val}")
    def plus_1():
        def_plus_1(val + 1)


def_plus_1(0)


@neetbox.action(name="action-2")
def action_2(text1, text2):
    logger.log(f"action 2 triggered. text1 = {text1}, text2 = {text2}")


@neetbox.action(name="wait-for-sec", blocking=False)
def wait_for_sec(sec):
    sec = int(sec)
    logger.log(f"wait for {sec} sec.")
    time.sleep(sec)


@neetbox.action(name="block-for-sec", blocking=True)
def block_for_sec(sec):
    sec = int(sec)
    logger.log(f"block for {sec} sec.")
    time.sleep(sec)


@neetbox.action(name="eval")
def eval_code(code: str):
    logger.log(f"running code {code}")
    logger.info("eval result: ", eval(code))


_id_indexer = 0


@neetbox.action()
def new_action(id: int):
    global _id_indexer

    @neetbox.action(name=f"new_action_{_id_indexer}")
    def action_():
        pass

    _id_indexer += 1


@neetbox.action(name="shutdown", description="shutdown your process", blocking=True)
def sys_exit():
    logger.log("shutdown received, shutting down immediately.")
    os._exit(0)


@neetbox.action()
def send_image():
    from PIL import Image

    with Image.open("weight_visualize_conv1_0_1.png") as logo_image:
        neetbox.add_image(name="weights visualize", image=logo_image)


@logger.mention()
def test_mention(text: str):
    return text


@neetbox.action()
def run_test_mention(text: str):
    test_mention(text)


for i in range(99999):
    sleep(1)
    train(i)
