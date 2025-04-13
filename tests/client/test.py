import math
import os
import time
from random import random

import numpy as np

import neetbox
from neetbox import logger


@neetbox.action(name="action-1")
def print_text_to_console(text: str):
    """take action 1

    Args:
        text (string): print this string to console as log
    """

    logger.log(f"action 1 triggered. text = {text}")


@neetbox.action()
def action_bool(enable: bool):
    logger.info(f"action_bool triggered. enable = {enable}")
    return {"enable": enable}


def def_plus_1(val):
    @neetbox.action(name="plus1", description=f"val={val}")
    def plus_1():
        def_plus_1(val + 1)


def_plus_1(0)


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

    @neetbox.action(name=f"empty_action_{_id_indexer}")
    def action_():
        """this action does nothing"""
        pass

    _id_indexer += 1


@neetbox.action(name="shutdown", description="shutdown your process", blocking=True)
def sys_exit():
    logger.log("shutdown received, shutting down immediately.")
    os._exit(0)


@neetbox.action(name="Generate random noise image")
def send_image(width=400, height=300, num_channels=3):
    """Send a random noise image from numpy.array.

    If nc is 1, the Grayscale image will be created.
    If nc is 3, the RGB image will be generated.

    Args:
        nc (int): (1 or 3) number of channels.
        width (int): width of output image.
        height (int): height of output image.
    """
    from PIL import Image

    img = (np.random.rand(height, width, num_channels) * 255).astype(np.uint8)
    if num_channels == 3:
        img = Image.fromarray(img, mode="RGB")
    elif num_channels == 1:
        img = Image.fromarray(np.squeeze(img), mode="L")
    else:
        raise ValueError(f"Input nc should be 1/3. Got {num_channels}.")
    neetbox.add_image(name="random noise", image=img)


@logger.mention()
def test_mention(text: str):
    return text


@neetbox.action()
def run_test_mention(text: str):
    test_mention(text)


@neetbox.watch("train")
def train(step):
    loss, acc = random(), random()
    neetbox.add_scalar("sin", step, math.sin(step * 0.1))
    neetbox.add_scalar("cos", step, math.cos(step * 0.1))
    return {"global_step": step, "loss": loss, "acc": acc}


@neetbox.listen("train")  # listen to train
def print_to_console(metrix):
    logger.log(f"metrix from train: {metrix}")


@neetbox.watch("log-some-prefix", initiative=False, interval=5.0)  # run each 5 secs
def log_with_some_prefix():
    logger.ok("some ok")
    logger.info("some info")
    logger.debug("some debug")
    logger.warn("some warn")
    logger.err("some error")


train_config = {"epoch": 50, "batch_size": 10}


def simulate_train(config):
    epoch = config["epoch"]
    batch_size = config["batch_size"]
    with neetbox.progress(epoch) as e:
        for i in e:
            for j in neetbox.progress(batch_size):
                time.sleep(1)
                train(i * batch_size + j)


if __name__ == "__main__":
    neetbox.add_hyperparams(train_config)
    neetbox.set_run_name("test run")
    simulate_train(train_config)
