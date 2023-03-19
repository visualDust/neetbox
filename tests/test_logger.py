from neetbox.logging import logger

logger.info("loginfo")
logger.warn("logwarn")
logger.err("logerr")

def a():
    logger.log("Hello from the default logger")
    
class A():
    def a(self):
        logger.log("Hello from the default logger")

A().a()

from neetbox.logging.logger import get_logger
logger = get_logger("someone")
logger.set_log_dir("./logdir")
logger.log("someone said 1")
def b():
    logger.log("a")
def c():
    b()
    logger.log("b")
c()
logger.log("someone said 2")

class B:
    def b(self):
        self.logger = get_logger(self)
        self.logger.log("from class B")
        
B().b()