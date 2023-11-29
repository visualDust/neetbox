import { useAtom } from "jotai";
import { getProject } from "../services/projects";

export function useProjectStatus(name: string) {
  const project = getProject(name);
  const [data] = useAtom(project.status.atom);
  return data;
}

export function useProjectLogs(name: string) {
  const project = getProject(name);
  const [data] = useAtom(project?.logs.atom);
  return data;
}
