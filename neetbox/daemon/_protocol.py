from dataclasses import dataclass
from typing import Any

FRONTEND_API_ROOT = "/web"
CLIENT_API_ROOT = "/cli"


EVENT_TYPE_NAME_KEY = "event-type"
EVENT_ID_NAME_KEY = "event-id"
NAME_NAME_KEY = "name"
PAYLOAD_NAME_KEY = "payload"


@dataclass
class WsMsg:
    name: str
    event_type: str
    payload: Any
    event_id: int = -1

    def json(self):
        return {
            NAME_NAME_KEY: self.name,
            EVENT_TYPE_NAME_KEY: self.event_type,
            EVENT_ID_NAME_KEY: self.event_id,
            PAYLOAD_NAME_KEY: self.payload,
        }
