from neetbox.utils import package
from neetbox.integrations import engine
assert package.is_installed(engine.Torch, terminate=True)
