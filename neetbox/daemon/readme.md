# DAEMON readme

## WS message standard

websocke messages are described in json. There is a dataclass representing websocket message:

```python
@dataclass
class WsMsg:
    event_type: str
    payload: Any
    event_id: int = -1

    def json(self):
        return {
            EVENT_TYPE_NAME_KEY: self.event_type,
            EVENT_ID_NAME_KEY: self.event_id,
            PAYLOAD_NAME_KEY: self.payload,
        }
```

```json
{
    "event-type" : ...,
    "payload" : ...,
    "event-id" : ...
}
```

|    key     | value type |                      description                       |
| :--------: | :--------: | :----------------------------------------------------: |
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
      "action" : {...json representing action trigger...}
    },
    "event-id" : x
}
```

front may want to know the result of action. for example, whether the action was invoked successfully. therefore, `event-id` is necessary for cli to shape a ack response.

### cli acks frontend action query

cli execute action query(s) from frontend, and gives response by sending ack:

```json
{
    "event-type" : "ack",
    "name": "project name",
    "payload" : {
      "action" : {...json representing action result...}
    },
    "event-id" : x
}
```

where `event-id` is same as received action query.

---

Those are only examples. use them wisely.
