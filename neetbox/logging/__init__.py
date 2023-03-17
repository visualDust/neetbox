from .logger import get_logger
from .logger import Logger


class _logger_producer(Logger):
    def __init__(self) -> None:
        self.initialized = False
    
    

__all__ = ["get_logger"]