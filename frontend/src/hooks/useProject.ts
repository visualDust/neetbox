import { useAtom } from "jotai";
import { createContext, useContext } from "react";
import { getProject } from "../services/projects";

export const ProjectContext = createContext<{ projectId: string; projectName?: string } | null>(null);

export function useCurrentProject() {
  return useContext(ProjectContext);
}

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

export function useProjectImages(id: string) {
  const project = getProject(id);
  const [data] = useAtom(project?.images.atom);
  return data;
}
