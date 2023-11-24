import pytest

pytest.skip(allow_module_level=True)

from random import random
from time import sleep

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


for i in range(99999):
    sleep(1)
    train(i)
