from ._client_action_agent import _NeetActionManager as NeetActionManager
from ._image import impost

action = NeetActionManager.register

__all__ = ["impost", "action", "NeetActionManager"]
