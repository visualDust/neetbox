import { WsClient } from "./projectWebsocket";
import { LogData } from "./types";
import { checkLogForNotification } from "./logNotifications";

const projects = new Map<string, Project>();

export class Project {
  wsClient: WsClient;
  name: string | null = null;

  get nameOrId() {
    return this.name ?? this.id;
  }

  constructor(readonly id: string) {
    this.wsClient = new WsClient(this);
  }

  handleLog(log: LogData) {
    checkLogForNotification(log, this);
  }

  sendAction(action: string, args: Record<string, string>, onReply?: (result: { error; result }) => void) {
    this.wsClient.send(
      {
        "event-type": "action",
        payload: {
          name: action,
          args,
        },
      },
      onReply &&
        ((msg) => {
          onReply(msg.payload as any);
        }),
    );
  }
}

export function getProject(id: string) {
  let project = projects.get(id);
  if (!project) {
    project = new Project(id);
    projects.set(id, project);
  }
  return project;
}

export function startBackgroundTasks() {
  return {
    dispose: () => {
      for (const [name, project] of projects) {
        projects.delete(name);
        project.wsClient.ws.close();
      }
    },
  };
}
