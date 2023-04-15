import os
import toml
from neetbox.config import default as default_config, get_module_level_config
from neetbox.config._config import update_with
from neetbox.daemon import _try_attach_daemon
from neetbox.utils.framing import get_frame_module_traceback

module = get_frame_module_traceback(1).__name__
config_file_name = f"{module}.toml"


def post_init():
    import setproctitle

    project_name = get_module_level_config()["name"]
    setproctitle.setproctitle(project_name)


def init(path=None, load=False, **kwargs) -> bool:
    if path:
        os.chdir(path=path)
    current_path = os.getcwd()
    config_file_path = os.path.join(current_path, config_file_name)

    if not load:
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        if not os.path.isfile(config_file_path):  # config file not exist
            try:  # creating config file using default config
                with open(config_file_path, "w+") as config_file:
                    _config = dict(default_config)
                    if "name" in kwargs and kwargs["name"]:  # using given name
                        _config["name"] = kwargs["name"]
                    else:  # using the folder name
                        _config["name"] = os.path.basename(
                            os.path.normpath(os.getcwd())
                        )
                    toml.dump(_config, config_file)
                logger.ok(f"Workspace config created as {config_file_path}.")
                return True
            except Exception as e:
                logger.err(f"Failed to create {config_file_path}: {e}")
                return False
        else:  # config file exist:
            logger.err((f"Config file already exists."))
            return False
    else:  # if load only
        if not os.path.isfile(config_file_path):  # but config file not exist
            from neetbox.logging.logger import Logger

            logger = Logger("NEETBOX")  # builtin standalone logger
            logger.err(f"Config file {config_file_path} not exists.")
            return False

    try:  # do load only
        load_config = toml.load(config_file_path)
        update_with(load_config)
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        logger.ok(f"Loaded workspace config from {config_file_path}.")
        _try_attach_daemon()  # try attach daemon
        post_init()
        return True
    except Exception as e:
        from neetbox.logging.logger import Logger

        logger = Logger("NEETBOX")  # builtin standalone logger
        logger.err(f"Failed to load config from {config_file_path}: {e}")
        return False


if os.path.isfile(config_file_name):  # if in a workspace
    init(load=True)
