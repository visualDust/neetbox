import { useAtom } from "jotai";
import { createContext, useContext, useEffect } from "react";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";

export const ProjectContext = createContext<{
  projectId: string;
  projectName?: string;
  runId?: string;
  setRunId: (runId: string) => void;
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

export function useProjectWebSocket<T extends WsMsg["event-type"]>(
  id: string,
  type: T | null,
  onMessage: (msg: Extract<WsMsg, { "event-type": T }>) => void,
) {
  const project = getProject(id);
  useEffect(() => {
    const handle: typeof onMessage = (msg) => {
      if (!type || msg["event-type"] == type) {
        onMessage(msg);
      }
    };
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    project.wsClient.wsListeners.add(handle as any);
    // eslint-disable-next-line @typescript-eslint/no-explicit-any
    return () => void project.wsClient.wsListeners.delete(handle as any);
  }, [project, type, onMessage]);
}
