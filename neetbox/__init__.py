from neetbox.core import env, Engine
from neetbox.logging import get_logger

logger = get_logger("NEETBOX")

assert env.installed(Engine.Torch, terminate=True)
