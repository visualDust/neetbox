from neetbox.logging.logger import DEFAULT_LOGGER as logger
from neetbox.config import get_module_level_config
_cfg = get_module_level_config()
logger.set_log_dir(_cfg['logdir'])
from neetbox.logging.logger import LogSplitStrategies, LogMetadata, SplitStrategyCallable

__all__ = ["logger", 'LogSplitStrategies']
