WORKSPACE_CONFIG:dict = {}

def _update(cfg:dict):
    global WORKSPACE_CONFIG
    WORKSPACE_CONFIG.update(cfg)
    
def _get():
    global WORKSPACE_CONFIG
    return WORKSPACE_CONFIG