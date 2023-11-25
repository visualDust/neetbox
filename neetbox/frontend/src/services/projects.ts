import { atom, useAtom } from "jotai";
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
    }>,
    gpus: Array<{
      id: number;
      name: string,
      load: number;
      memoryUtil: number;
      memoryTotal: number;
      memoryFree: number;
      memoryUsed: number;
      temperature: number;
      driver: string;
    }>
    ram: {
      total: number,
      available: number,
      used: number,
      free: number,
    }
  }>;
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
const nullProjectAtom = atom<Project>(null!);

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
      const data = await res.json();
      const projectData = { ...this.status.value };
      projectData.current = data;
      projectData.history = slideWindow(projectData.history, data, 60);
      this.status.value = projectData;
    });
  }

  handleLog(log: LogData) {
    this.logs.value = slideWindow(this.logs.value, log, 200); // TODO
  }
}

export function getOrAddProject(name: string) {
  let project = projects.get(name);
  if (!project) {
    project = new Project(name);
    projects.set(name, project);
  }
  return project;
}

export function useProjectStatus(name: string) {
  const project = getOrAddProject(name);
  const [data] = useAtom(project?.status.atom ?? nullProjectAtom);
  return data;
}

export function useProjectLogs(name: string) {
  const project = getOrAddProject(name);
  const [data] = useAtom(project?.logs.atom);
  return data;
}

export function startBackgroundTasks() {
  function updateAllProjectsData() {
    for (const project of projects.values()) {
      project.updateData();
    }
  }
  const timer = setInterval(updateAllProjectsData, 1000);
  return {
    stop: () => clearInterval(timer),
  };
}

function slideWindow<T>(arr: T[], item: T, max: number) {
  arr = arr.slice(arr.length + 1 > max ? arr.length + 1 - max : 0);
  arr.push(item);
  return arr;
}
