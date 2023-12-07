# Testing DAEMON

NEETBOX daemon consists of client side and server side. While client side syncs status of running project and platform information including hardware, server side provides apis for status monitoring and websocket forcasting between client and frontends.

Basically neetbox will also launch a backend on localhost when a project launching configured with daemon server address at localhost. The server will run in background without any output, and you may want to run a server with output for debug purposes.

## How to test neetbox server

at neetbox project root:

```bash
python neetbox/daemon/server/_server.py
```

script above should launch a server in debug mode on `localhost:5000`, it wont read the port in `neetbox.toml`. a swegger UI is provided at [localhost:5000/docs](http://127.0.0.1:5000/docs) in debug mode. websocket server should run on port `5001`.

If you want to simulate a basic neetbox client sending message to server, at neetbox project root:

```bash
cd tests/client
python test.py
```

script above should launch a simple case of neetbox project with some logs and status sending to server.

## Websocket message standard

websocke messages are described in json. There is a dataclass representing websocket message:

```python
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
```

```json
{
    "name" : ...,
    "event-type" : ...,
    "payload" : ...,
    "event-id" : ...
}
```

an simple websocket message should include:

|    key     | value type |                      description                       |
| :--------: | :--------: | :----------------------------------------------------: |
|    name    |   string   |                      project name                      |
| event-type |   string   |            indicate type of data in payload            |
|  payload   |   string   |                      actual data                       |
|  event-id  |    int     | for events who need ack. default -1 means no event id. |

## Event types

the table is increasing. a frequent check would keep you up to date.

| event-type |      accepting direction      |                            means                             |
| :--------: | :---------------------------: | :----------------------------------------------------------: |
| handshake  | cli <--> server <--> frontend |  string in `payload` indicate connection type ('cli'/'web')  |
|    log     |   cli -> server -> frontend   |                 `payload` contains log data                  |
|   action   |   cli <- server <- frontend   |              `payload` contains action trigger               |
|    ack     | cli <--> server <--> frontend | `payload` contains ack, and `event-id` should be a valid key |

## Examples of websocket data

### handshake

for instance, frontend connected to server. frontend should report connection type immediately by sending:

```json
{
  "event-type": "handshake",
  "name": "project name",
  "payload": {
    "who": "web"
  },
  "event-id": X
}
```

where `event-id` is used to send ack to the starter of the connection, it should be a random int value.

### cli sending log to frontend

cli sents log(s) via websocket, server will receives and broadcast this message to related frontends. cli should send:

```json
{
  "event-type": "log",
  "name": "project name",
  "payload": {
    "log" : {...json representing log data...}
  },
  "event-id": -1
}
```

where `event-id` is a useless segment, leave it default. it's okay if nobody receives log.

### frontend(s) querys action to cli

frontend send action request to server, and server will forwards the message to cli. frontend should send:

```json
{
    "event-type" : "action",
    "name": "project name",
    "payload" : {
      "name" : <name of action>,
      "args" : {...arg names and values...}
    },
    "event-id" : x
}
```

front may want to know the result of action. for example, whether the action was invoked successfully. therefore, `event-id` is necessary for cli to shape a ack response.

### cli acks frontend action query

cli execute action query(s) from frontend, and gives response by sending ack:

```json
{
    "event-type" : "action",
    "name": "project name",
    "payload" : {
      "name" : <name of action>,
      "result" : <returned value of cation>
    },
    "event-id" : x
}
```

> CAUTION !
>
> - frontend should look for list of actions via `/status` api instead of websocket.
> - when **frontend** receive websocket message with `event-type` = `action`, it must be the action result returned from client.
> - when **client** receive websocket message with `event-type` = `action`, it must be the action queried by frontend.
> - only actions with `blocking` = `true` could return result to frontend.

where `event-id` is same as received action query.

---

Those are only examples. use them wisely.
