import { PrimitiveAtom, atom, getDefaultStore, useAtom } from "jotai";

interface WithTimestamp<T> {
  value: T;
  timestamp: number;
  interval: number;
}

export interface ProjectData {
  platform: WithTimestamp<Record<string, string | string[]>>;
  hardware: WithTimestamp<{
    cpus: Array<{
      id: number;
      percent: number;
      freq: [current: number, min: number, max: number];
    }>;
  }>;
  train: WithTimestamp<Record<string, unknown>>;
}

interface ProjectPollData {
  enablePolling: boolean;
  data?: ProjectData;
  history: Array<ProjectData>;
}

const projects = new Map<string, PrimitiveAtom<ProjectPollData>>();
const nullProjectAtom = atom<ProjectPollData>(null!);

export function addProject(name: string) {
  let projectAtom = projects.get(name);
  if (!projectAtom) {
    projectAtom = atom({
      enablePolling: true,
      data: null,
      history: [],
    } as any);
    projects.set(name, projectAtom);
  }
  return projectAtom;
}

export function useProjectData(name: string | null | undefined) {
  const projectAtom = name ? addProject(name) : nullProjectAtom;
  const [data] = useAtom(projectAtom);
  return data;
}

function updateAllProjectsData() {
  for (const [name, projectAtom] of projects) {
    fetch("/web/status/" + name).then(async (res) => {
      const data = await res.json();
      const project = { ...getDefaultStore().get(projectAtom) };
      project.data = data;
      project.history = slideWindow(project.history, data, 60);
      getDefaultStore().set(projectAtom, project);
    });
  }
}

setInterval(updateAllProjectsData, 1000);

function slideWindow<T>(arr: T[], item: T, max: number) {
  arr = arr.slice(arr.length + 1 > max ? arr.length + 1 - max : 0);
  arr.push(item);
  return arr;
}
