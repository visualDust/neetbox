from ._client_action_agent import _NeetActionManager as NeetActionManager
from ._image import add_image

action = NeetActionManager.register

__all__ = ["add_image", "action", "NeetActionManager"]
