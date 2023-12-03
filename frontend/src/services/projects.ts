import { BetterAtom } from "../utils/betterAtom";
import { WsClient } from "./projectWebsocket";
import { ProjectStatusHistory, LogData, ProjectStatus, ImageMetadata } from "./types";

const projects = new Map<string, Project>();

const StatusHistoryCount = 120;

export class Project {
  wsClient: WsClient;
  status = new BetterAtom<ProjectStatusHistory>({
    enablePolling: true,
    current: undefined,
    history: [],
  });
  logs = new BetterAtom<LogData[]>([]);
  images = new BetterAtom<ImageMetadata[]>([]);

  constructor(readonly id: string) {
    this.wsClient = new WsClient(this);

    fetch(
      "/web/status/" +
        this.id +
        "/history?" +
        new URLSearchParams({
          condition: JSON.stringify({
            order: { id: "DESC" },
            limit: StatusHistoryCount,
          }),
        }),
    ).then(async (res) => {
      const data = await res.json();
      console.info("history", data);
      data.sort((a, b) => a.id - b.id);
      this.status.value = { ...this.status.value, history: data.map((x) => x.metadata) };
    });
  }

  updateData() {
    if (!this.status.value.enablePolling) return false;

    fetch("/web/status/" + this.id).then(async (res) => {
      const data = (await res.json()) as ProjectStatus;
      data.hardware.value.cpus.forEach((cpu, idx) => {
        if (typeof cpu.id != "number" || cpu.id < 0) cpu.id = idx;
      });
      const projectData = { ...this.status.value };
      projectData.current = data;
      projectData.history = slideWindow(projectData.history, [data], StatusHistoryCount);
      this.status.value = projectData;
      console.info({ projectData });
    });
  }

  private _logQueue: LogData[] | null = null;
  private _logFlush = () => {
    this.logs.value = slideWindow(this.logs.value, this._logQueue!, 1000); // TODO
    this._logQueue = null;
  };

  handleLog(log: LogData) {
    if (!this._logQueue) {
      this._logQueue = [];
      setTimeout(this._logFlush, 60);
    }
    this._logQueue.push(log);
  }

  handleImage(image: ImageMetadata) {
    this.images.value = [...this.images.value, image];
  }

  sendAction(action: string, args: Record<string, string>, onReply?: (result: any) => void) {
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
          onReply(msg.payload);
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
  function updateAllProjectsData() {
    for (const project of projects.values()) {
      project.updateData();
    }
  }
  const timer = setInterval(updateAllProjectsData, 1000);
  return {
    dispose: () => {
      clearInterval(timer);
      for (const [name, project] of projects) {
        projects.delete(name);
        project.wsClient.ws.close();
      }
    },
  };
}

function slideWindow<T>(arr: T[], items: T[], max: number) {
  arr = arr.slice(arr.length + items.length > max ? arr.length + items.length - max : 0);
  arr.push(...items);
  return arr;
}
