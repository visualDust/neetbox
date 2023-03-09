from neetbox.logging import get_logger

_static_logger = get_logger(whom="NEETBOX")
def get_static_logger():
    return _static_logger

