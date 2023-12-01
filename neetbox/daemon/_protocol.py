from dataclasses import dataclass
from typing import Any

FRONTEND_API_ROOT = "/web"
CLIENT_API_ROOT = "/cli"


EVENT_TYPE_NAME_KEY = "event-type"
EVENT_ID_NAME_KEY = "event-id"
WORKSPACE_ID_KEY = "workspace-id"
PAYLOAD_NAME_KEY = "payload"


@dataclass
class WsMsg:
    project_id: str
    event_type: str
    payload: Any
    event_id: int = -1

    def json(self):
        return {
            WORKSPACE_ID_KEY: self.project_id,
            EVENT_TYPE_NAME_KEY: self.event_type,
            EVENT_ID_NAME_KEY: self.event_id,
            PAYLOAD_NAME_KEY: self.payload,
        }
