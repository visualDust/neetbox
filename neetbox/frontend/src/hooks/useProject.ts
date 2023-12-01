import { useAtom } from "jotai";
import { getProject } from "../services/projects";

export function useProjectStatus(id: string) {
  const project = getProject(id);
  const [data] = useAtom(project.status.atom);
  return data;
}

export function useProjectLogs(id: string) {
  const project = getProject(id);
  const [data] = useAtom(project?.logs.atom);
  return data;
}
