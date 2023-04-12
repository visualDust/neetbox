import collections


def _default_none():
    return None


DEFAULT_CONFIG = collections.defaultdict(_default_none)
DEFAULT_CONFIG.update({"logging": {"logdir": None}, "integrations": {}})

WORKSPACE_CONFIG: dict = DEFAULT_CONFIG.copy()


def _update(cfg: dict):
    global WORKSPACE_CONFIG
    WORKSPACE_CONFIG.update(cfg)


def _get():
    global WORKSPACE_CONFIG
    return WORKSPACE_CONFIG
