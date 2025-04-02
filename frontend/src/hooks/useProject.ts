import { createContext, useContext, useEffect } from "react";
import { useAtom } from "jotai";
import { KeyedMutator } from "swr";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";
import { useAPI } from "../services/api";
import { RunStatus } from "../services/types";
import { useProjectData } from "./useProjectData";

export { useProjectData };

export const ProjectContext = createContext<{
  projectId: string;
  projectName?: string;
  runId?: string;
  isOnlineRun: boolean;
} | null>(null);

export function useCurrentProject() {
  return useContext(ProjectContext)!;
}

export function useProjectStatus(id: string) {
  return useAPI(`/project/${id}`, { refreshInterval: 5000 });
}

export function useProjectRunIds(id: string) {
  const { data, mutate } = useAPI(`/project/${id}`, { refreshInterval: 5000 });
  return { data: data?.runids, mutate };
}

export function useProjectRunStatus(
  id: string,
  runId?: string,
): [data: RunStatus | undefined, mutate: KeyedMutator<any>] {
  const { data, mutate } = useAPI(`/project/${id}/run/${runId}`, { refreshInterval: 5000 });
  return [!runId ? undefined : data, mutate];
}

export function useProjectWebSocketReady(id: string) {
  const project = getProject(id);
  return useAtom(project.wsClient.isReady.atom)[0];
}

export function useProjectWebSocket<T extends WsMsg["eventType"]>(
  id: string,
  type: T | null,
  onMessage: (msg: Extract<WsMsg, { eventType: T }>) => void,
) {
  const project = getProject(id);
  useEffect(() => {
    const handle: typeof onMessage = (msg) => {
      if (!type || msg.eventType == type) {
        onMessage(msg);
      }
    };
    project.wsClient.wsListeners.add(handle as any);
    return () => void project.wsClient.wsListeners.delete(handle as any);
  }, [project, type, onMessage]);
}

export function useProjectSeries(projectId: string, runId: string, type: string) {
  return useProjectData({
    type: `${type}`,
    url: `/project/${projectId}/series/${type}?${new URLSearchParams({ runId: runId })}`,
    projectId,
    runId,
    transformWS: (msg) => msg.series,
    reducer: (data, queue) => [...new Set([...data, ...queue])],
  });
}
