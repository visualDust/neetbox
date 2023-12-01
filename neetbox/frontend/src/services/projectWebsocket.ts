import { WEBSOCKET_URL } from "./api";
import { Project } from "./projects";

interface WsMsg<Type extends string = string, Payload = any> {
  "event-type": Type;
  name: string;
  payload: Payload;
  "event-id": number;
}

export class WsClient {
  ws: WebSocket;
  nextId = ~~(Math.random() * 100000000) * 1000;
  callbacks = new Map<number, (msg: WsMsg) => void>();
  nextLogId = 1;

  constructor(readonly project: Project) {
    this.ws = new WebSocket(WEBSOCKET_URL);
    this.ws.onopen = () => {
      console.info("ws open");
      this.send({
        "event-type": "handshake",
        payload: {
          who: "web",
        },
      });
    };
    this.ws.onmessage = (e) => {
      // console.info("ws receive", e.data);
      const json = JSON.parse(e.data) as WsMsg;
      const eventId = json["event-id"];
      if (this.callbacks.has(eventId)) {
        this.callbacks.get(eventId)!(json);
        this.callbacks.delete(eventId);
      } else if (json["event-type"] === "log") {
        json.payload._id = this.nextLogId++;
        project.handleLog(json.payload);
      }
    };
  }

  send(msg: Omit<WsMsg, "name" | "event-id">, onReply?: (msg: WsMsg) => void) {
    const eventId = this.nextId++;
    const json = {
      ...msg,
      "workspace-id": this.project.id,
      "event-id": eventId,
    };
    console.info("ws send", json);
    this.ws.send(JSON.stringify(json));
    if (onReply) this.callbacks.set(eventId, onReply);
  }
}
