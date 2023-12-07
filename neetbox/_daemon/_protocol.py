from dataclasses import dataclass
from typing import Any

EVENT_TYPE_NAME_KEY = "event-type"
EVENT_ID_NAME_KEY = "event-id"
PROJECT_ID_KEY = WORKSPACE_ID_KEY = "projectid"
RUN_ID_KEY = "runid"
SERIES_ID_KEY = "series"
PAYLOAD_NAME_KEY = "payload"

# ===================== HTTP things =====================

FRONTEND_API_ROOT = "/web"
CLIENT_API_ROOT = "/cli"

# ===================== WsbSocket things =====================


@dataclass
class WsMsg:
    project_id: str
    event_type: str
    payload: Any
    event_id: int = -1

    def json(self):
        return {
            PROJECT_ID_KEY: self.project_id,
            EVENT_TYPE_NAME_KEY: self.event_type,
            EVENT_ID_NAME_KEY: self.event_id,
            PAYLOAD_NAME_KEY: self.payload,
        }
