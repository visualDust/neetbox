import { useAtom } from "jotai";
import { createContext, useContext, useEffect } from "react";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";

export const ProjectContext = createContext<{
  projectId: string;
  projectName?: string;
  runId?: string;
} | null>(null);

export function useCurrentProject() {
  return useContext(ProjectContext)!;
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

export function useProjectWebSocket(
  id: string,
  type: WsMsg["event-type"] | null,
  onMessage: (msg: WsMsg) => void,
) {
  const project = getProject(id);
  useEffect(() => {
    const handle: typeof onMessage = (msg) => {
      if (!type || msg["event-type"] == type) {
        onMessage(msg);
      }
    };
    project.wsClient.wsListeners.add(handle);
    return () => void project.wsClient.wsListeners.delete(handle);
  }, [project, type, onMessage]);
}
