"""
difference between neetbox.frontend and outside frontend directory:

- neetbox.frontend contains python codes that allows user to interact with backend(and of course frontend).
- outside frontend directory contains real directory codes, not python codes.
"""

from ._client_action_agent import _NeetActionManager as NeetActionManager
from ._image import impost

action = NeetActionManager.register

__all__ = ["impost", "action", "NeetActionManager"]
