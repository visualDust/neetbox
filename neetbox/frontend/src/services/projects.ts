import { BetterAtom } from "../utils/betterAtom";
import { WsClient } from "./projectWebsocket";

export interface ProjectStatusHistory {
  enablePolling: boolean;
  current?: ProjectStatus;
  history: Array<ProjectStatus>;
}

export interface ProjectStatus {
  platform: WithTimestamp<Record<string, string | string[]>>;
  hardware: WithTimestamp<{
    cpus: Array<{
      id: number;
      percent: number;
      freq: [current: number, min: number, max: number];
    }>;
    gpus: Array<{
      id: number;
      name: string;
      load: number;
      memoryUtil: number;
      memoryTotal: number;
      memoryFree: number;
      memoryUsed: number;
      temperature: number;
      driver: string;
    }>;
    ram: {
      total: number;
      available: number;
      used: number;
      free: number;
    };
  }>;
  __action: WithTimestamp<
    Record<
      string,
      {
        args: Record<string, string>;
        blocking: boolean;
        description: string;
      }
    >
  >;
}

export interface WithTimestamp<T> {
  value: T;
  timestamp: number;
  interval: number;
}

export interface LogData {
  prefix: string;
  datetime: string;
  whom: string;
  msg: string;
  /** frontend only */
  _id: number;
}

const projects = new Map<string, Project>();

export class Project {
  wsClient: WsClient;
  status: BetterAtom<ProjectStatusHistory>;
  logs: BetterAtom<LogData[]>;

  constructor(readonly name: string) {
    this.wsClient = new WsClient(this);
    this.status = new BetterAtom({
      enablePolling: true,
      current: undefined,
      history: [],
    } as ProjectStatusHistory);
    this.logs = new BetterAtom([] as LogData[]);
  }

  updateData() {
    if (!this.status.value.enablePolling) return false;

    fetch("/web/status/" + this.name).then(async (res) => {
      const data = (await res.json()) as ProjectStatus;
      data.hardware.value.cpus.forEach((cpu, idx) => {
        if (typeof cpu.id != "number" || cpu.id < 0) cpu.id = idx;
      });
      const projectData = { ...this.status.value };
      projectData.current = data;
      projectData.history = slideWindow(projectData.history, data, 70);
      this.status.value = projectData;
    });
  }

  handleLog(log: LogData) {
    this.logs.value = slideWindow(this.logs.value, log, 200); // TODO
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

export function getProject(name: string) {
  let project = projects.get(name);
  if (!project) {
    project = new Project(name);
    projects.set(name, project);
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

function slideWindow<T>(arr: T[], item: T, max: number) {
  arr = arr.slice(arr.length + 1 > max ? arr.length + 1 - max : 0);
  arr.push(item);
  return arr;
}
