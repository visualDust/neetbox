def test_default_logger():
    from neetbox.logging import logger
    logger.banner('neetbox')

    logger.info("loginfo")
    logger.warn("logwarn")
    logger.err("logerr")

    def a():
        logger.log("Hello from the default logger")

    class A:
        def a(self):
            logger.log("Hello from the default logger")

    A().a()


def test_logger_with_specific_identity():
    from neetbox.logging import logger

    logger = logger("someone")
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
            self.logger = logger(self)
            self.logger.log("from class B")

    B().b()


def test_out_of_dated():
    from neetbox.logging import get_logger

    logger = get_logger("someone")
    logger.log("someone said 1")


def test_logger_catch():
    from neetbox.logging import logger

    @logger.catch(reraise=False)
    def my_function(x, y, z):
        # An error? It's caught anyway!
        return 1 / (x + y + z)

    my_function(0, 0, 0)
