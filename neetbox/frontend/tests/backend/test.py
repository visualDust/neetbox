from neetbox.pipeline import watch, listen
from neetbox.logging import logger
from neetbox.integrations.environment import hardware
from neetbox.integrations.environment import platform
from neetbox.daemon import action
from random import random
from time import sleep


@watch("train", initiative=True)
def train(epoch):

    @action.register()
    def some_action_in_train():
        print("some_action running " + epoch)

    loss, acc = random(), random()
    return {"loss": loss, "acc": acc}

@action.register()
def some_action_1():
    print("some_action running")

@listen("train")
def print_to_console(metrix):

    logger.log(f"metrix from train: {metrix}")


for i in range(99999):
    sleep(1)
    train(i)
