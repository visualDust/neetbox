from neetbox.core import env
from neetbox.integrations import engine
assert env.installed(engine.Torch, terminate=True)
