import time

from tqdm import tqdm

import neetbox
from neetbox import logger


def a():
    logger.log("running a")


def b():
    logger.log("running b")


def c():
    logger.log("running c")


def d():
    logger.log("running d")


def e():
    logger.log("running e")


with tqdm(neetbox.progress(50)) as progress:
    for _ in progress:
        for func in neetbox.progress([a, b, c, d, e]):
            func()
            time.sleep(1)
