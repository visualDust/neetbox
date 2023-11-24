from neetbox.config import get_module_level_config
from neetbox.logging.logger import DEFAULT_LOGGER as logger
from neetbox.logging.logger import set_log_level

_cfg = get_module_level_config()
logger.set_log_dir(_cfg["logdir"])
set_log_level(_cfg["level"])

__all__ = ["logger"]
