from neetbox.config import get_module_level_config
from neetbox.logging.logger import DEFAULT_LOGGER as logger

_cfg = get_module_level_config()
logger.set_log_dir(_cfg["logdir"])
from neetbox.logging.logger import LogSplitStrategies

__all__ = ["logger", "LogSplitStrategies"]
