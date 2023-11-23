class LogWriter:
    def write(self, raw_msg):
        pass


class ConsoleLogWriter(metaclass=LogWriter):
    def __init__(self) -> None:
        pass

    def write(self, raw_msg):
        pass


class FileLogWriter(metaclass=LogWriter):
    def __init__(self) -> None:
        pass

    def write(self, raw_msg):
        pass


class WebSocketLogWriter(metaclass=LogWriter):
    def __init__(self) -> None:
        pass

    def write(self, raw_msg):
        pass
