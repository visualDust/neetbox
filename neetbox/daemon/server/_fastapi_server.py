from typing import Any, Dict, List

import uvicorn
from fastapi import FastAPI, HTTPException, WebSocket
from pydantic import BaseModel
from starlette.endpoints import WebSocketEndpoint

FRONTEND_API_ROOT = "/web"
CLIENT_API_ROOT = "/cli"

app = FastAPI()


# ===============================================================
# Client functions (backend)
# ===============================================================


class ClientEndpoint(WebSocketEndpoint):
    encoding = "json"
    subscriptions: Dict[str, List[WebSocket]] = {}
    socket_pool: Dict[str, WebSocket] = {}

    def __init__(self, scope, receive, send, name: str):
        super().__init__(scope, receive, send)
        self.name = name

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        ClientEndpoint.socket_pool[self.name] = websocket  # add to socket pool

    async def on_receive(self, websocket: WebSocket, data: Any):
        """
                    ┌────►Viewer
                    │
                    │
        Client─────►Center──►Viewer
                    │
                    │
                    └────►Viewer
        """
        for ws in ClientEndpoint.subscriptions[self.name]:
            await ws.send_json(data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        pass

    @staticmethod
    def subscribe(websocket: WebSocket, name: str):
        if name not in ClientEndpoint.subscriptions.keys():
            ClientEndpoint.subscriptions[name] = []
        ClientEndpoint.subscriptions[name].append(websocket)


@app.websocket(f"{CLIENT_API_ROOT}" + "/ws/")
async def handle_client_websocket(websocket: WebSocket, name: str):
    await ClientEndpoint(websocket.scope, websocket.receive, websocket.send, name)


class Client(BaseModel):
    status: dict = {}


class ClientManager:
    def __init__(self) -> None:
        self._client_registry: Dict[str, Client] = {}

    def register(self, name: str, client: Client):
        if name in self._client_registry.keys():
            raise ValueError(f"Client with name {name} already exists.")
        self._client_registry[name] = client

    def get(self, name: str):
        return self._client_registry[name]

    def get_all(self):
        return self._client_registry


client_manager = ClientManager()


@app.get("/register/")
async def register_client(name: str):
    try:
        client_manager.register(name, Client())
    except ValueError:
        raise HTTPException(status_code=400, detail="Client already exists.")


class Status(BaseModel):
    status: dict = {}


@app.post(f"{CLIENT_API_ROOT}" + "/sync/")
async def sync_client(name: str, status: Status):
    try:
        client = client_manager.get(name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found.")
    client.status = status.status


# ===============================================================
# Viewer functions (frontend)
# ===============================================================


class ViewerEndpoint(WebSocketEndpoint):
    encoding = "json"

    def __init__(self, scope, receive, send, name: str):
        super().__init__(scope, receive, send)
        self.name = name

    async def on_connect(self, websocket: WebSocket):
        await websocket.accept()
        ClientEndpoint.subscribe(websocket, self.name)

    async def on_receive(self, websocket: WebSocket, data: Any):
        """
        Viewer─────►Center─────►Client
        """
        await ClientEndpoint.socket_pool[self.name].send_json(data)

    async def on_disconnect(self, websocket: WebSocket, close_code: int):
        ClientEndpoint.subscriptions[self.name].remove(websocket)  # remove from subscription


@app.websocket(f"{FRONTEND_API_ROOT}" + "/ws/")
async def handle_viewer_websocket(websocket: WebSocket, name: str):
    await ViewerEndpoint(websocket.scope, websocket.receive, websocket.send, name)


class ClientList(BaseModel):
    names: List[str]


@app.get(f"{FRONTEND_API_ROOT}" + "/list", response_model=ClientList)
async def return_names_of_status():
    return client_manager.get_all().keys()


@app.get(f"{FRONTEND_API_ROOT}" + "/status/", response_model=Status)
async def return_status_of(name: str):
    try:
        client = client_manager.get(name)
    except ValueError:
        raise HTTPException(status_code=404, detail="Client not found.")
    return client.status


if __name__ == "__main__":
    cfg = {"port": 5000, "host": ""}
    uvicorn.run("_fastapi_server:app", host=cfg["host"], port=cfg["port"], reload=True)
