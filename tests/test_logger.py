def test_default_logger():
    from neetbox.logging import logger

    # logger.banner('neetbox')

    logger.info("loginfo")
    logger.warn("logwarn")
    logger.err("logerr")

    @logger.mention
    def a():
        logger.log("Hello from the default logger")

    a()


def test_logger_with_specific_identity():
    from neetbox.logging import logger

    logger = logger("someone")
    logger.set_log_dir("./log")
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
