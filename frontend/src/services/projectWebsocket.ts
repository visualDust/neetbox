import { WEBSOCKET_URL } from "./api";
import { Project } from "./projects";
import { ImageMetadata } from "./types";

export interface WsMsgBase<Type extends string = string, Payload = undefined> {
  "event-type": Type;
  name: string;
  payload: Payload;
  "event-id": number;
  who: "web" | "cli";
  projectid: string;
  runid: string;
  timestamp: string;
}

export type WsMsg =
  | WsMsgBase
  | WsMsgBase<"handshake">
  | (WsMsgBase<"image"> & ImageMetadata)
  | WsMsgBase<"scalar", { series: string; x: number; y: number }>
  | WsMsgBase<
      "log",
      {
        message: string;
        series: string;
        whom: string;
      }
    >;

export class WsClient {
  ws: WebSocket;
  nextId = ~~(Math.random() * 100000000) * 1000;
  callbacks = new Map<number, (msg: WsMsg) => void>();
  wsListeners = new Set<(msg: WsMsg) => void>();

  constructor(readonly project: Project) {
    this.ws = new WebSocket(WEBSOCKET_URL);
    this.ws.onopen = () => {
      console.info("ws open");
      this.send({
        "event-type": "handshake",
        who: "web",
      });
    };
    this.ws.onmessage = (e) => {
      const json = JSON.parse(e.data) as WsMsg;
      console.info("ws receive", json);
      const eventId = json["event-id"];
      const eventType = json["event-type"];
      if (this.callbacks.has(eventId)) {
        this.callbacks.get(eventId)!(json);
        this.callbacks.delete(eventId);
      } else if (eventType === "log") {
        project.handleLog({
          whom: json.payload?.whom,
          datetime: json.timestamp,
          msg: json.payload?.message,
          series: json.payload?.series,
        });
      } else {
        // console.warn("ws unhandled message", json);
        this.wsListeners.forEach((x) => x(json));
      }
    };
  }

  send(msg: Omit<WsMsg, "name" | "event-id" | "projectid" | "runid">, onReply?: (msg: WsMsg) => void) {
    const eventId = this.nextId++;
    const json = {
      ...msg,
      projectid: this.project.id,
      "event-id": eventId,
    };
    console.info("ws send", json);
    this.ws.send(JSON.stringify(json));
    if (onReply) this.callbacks.set(eventId, onReply);
  }
}
