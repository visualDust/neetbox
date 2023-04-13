from neetbox.daemon._daemon_client import connect_daemon, watch
from neetbox.daemon._daemon import daemon_process
from neetbox.logging import logger
import daemon
import time

def __attach_daemon(daemon_config):
    try:
        __IPYTHON__    
    except NameError:
        pass
    else:
        return # ignore if debugging in ipython
    _online_status = connect_daemon(daemon_config) # try to connect daemon
    if not _online_status: # if no daemon online
        logger.log(f"No daemon running at {daemon_config['server']}:{daemon_config['port']}, trying to create daemon...")
        with daemon.DaemonContext():
            daemon_process(daemon_config) # create daemon
        time.sleep(1)
        connect_daemon(daemon_config) # try connect daemon

def _try_attach_daemon():
    from neetbox.config import get_module_level_config
    _cfg = get_module_level_config()
    if _cfg['enable']:
        __attach_daemon(_cfg)

__all__ = ['watch','_try_attach_daemon']
