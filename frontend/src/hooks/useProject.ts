import { createContext, useContext, useEffect, useMemo, useState } from "react";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";
import { fetcher, useAPI } from "../services/api";
import { Condition, createCondition } from "../utils/condition";

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
  const { data } = useAPI(`/project/${id}`);
  return data;
}

export function useProjectRunStatus(id: string, runId?: string) {
  const data = useProjectStatus(id);
  return !runId ? undefined : data?.status[runId];
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

export function useProjectData<T = any>(options: {
  type: string;
  projectId: string;
  runId?: string;
  limit?: number;
  conditions?: Condition;
  filterWS?: (msg: any) => boolean;
  transformHTTP?: (data: any) => unknown;
  transformWS?: (data: any) => unknown;
  onNewWSData?: (transformed: any) => void;
}) {
  const { type, projectId, runId, limit, transformWS = (x) => x, transformHTTP = (x) => x } = options;
  const { data, mutate } = useAPI(
    `/${type}/${projectId}/history?${createCondition({
      runId,
      ...(!limit ? null : { limit, order: { id: "DESC" } }),
      ...options.conditions,
    })}`,
    {
      fetcher: async (url) => {
        let result = (await fetcher(url)).map(transformHTTP);
        if (limit) {
          result = result.reverse();
        }
        return result;
      },
    },
  );
  const [realtimeData, setRealtimeData] = useState<any[]>([]);
  useProjectWebSocket(projectId, type, (msg) => {
    if (!runId || (msg.runid == runId && (!options.filterWS || options.filterWS(msg)))) {
      const transformed = transformWS(msg);
      // if (data) {
      //   mutate((arr) => [...arr, transformed], { revalidate: false });
      // } else {
      //   setRealtimeData((arr) => [...arr, transformed]);
      // }
      if (data) {
        mutate((arr) => [...arr, transformed], { revalidate: false });
        options.onNewWSData?.(transformed);
      }
      // setRealtimeData((arr) => [...arr, transformed]);
    }
  });
  // useEffect(() => {
  //   if (data && realtimeData.length) {
  //     setRealtimeData([]);
  //     mutate([...data, ...realtimeData], { revalidate: false });
  //   }
  // }, [data, realtimeData]);
  console.debug("useProjectData", options.type, { data, realtimeData });
  return useMemo(() => (data ? ([...data, ...realtimeData] as T[]) : null), [data, realtimeData]);
}
