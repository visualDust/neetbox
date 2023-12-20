import { createContext, useContext, useEffect, useState } from "react";
import { useAtom } from "jotai";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";
import { fetcher, useAPI } from "../services/api";
import { Condition, createCondition } from "../utils/condition";
import { RunStatus } from "../services/types";
import { slideWindow } from "../utils/array";
import { IdleTimer } from "../utils/timer";

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

export function useProjectRunStatus(id: string, runId?: string): RunStatus | undefined {
  const { data } = useAPI(`/project/${id}/run/${runId}`, { refreshInterval: 5000 });
  return !runId ? undefined : data;
}

export function useProjectWebSocketReady(id: string) {
  const project = getProject(id);
  return useAtom(project.wsClient.isReady.atom)[0];
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
    project.wsClient.wsListeners.add(handle as any);
    return () => void project.wsClient.wsListeners.delete(handle as any);
  }, [project, type, onMessage]);
}

export function useProjectSeries(projectId: string, runId: string, type: string) {
  return useProjectData({
    type: `${type}`,
    url: `/project/${projectId}/series/${type}?${new URLSearchParams({ runid: runId })}`,
    projectId,
    runId,
    transformWS: (msg) => msg.series,
    reducer: (data, queue) => [...new Set([...data, ...queue])],
  });
}

export function useProjectData<T = any>(options: {
  type: string;
  url?: string;
  disable?: boolean;
  projectId: string;
  runId?: string;
  limit?: number;
  conditions?: Condition;
  reverse?: boolean;
  filterWS?: (msg) => boolean;
  transformHTTP?: (data) => unknown;
  transformWS?: (msg) => unknown;
  reducer?: (data: T[], queue: T[]) => T[];
}) {
  const { type, projectId, runId, limit, url: customUrl } = options;

  const wsReady = useProjectWebSocketReady(projectId);

  const url =
    options.disable || !wsReady
      ? null
      : customUrl ??
        `/project/${projectId}/${type}?${createCondition({
          runId,
          ...(!limit ? null : { limit, order: { id: "DESC" } }),
          ...options.conditions,
        })}`;

  const [renderData, setRenderData] = useState<T[] | null>(null);

  useEffect(() => {
    if (!url) {
      if (renderData) setRenderData(null);
      return;
    }

    const { transformWS = (x) => x, transformHTTP = (x) => x, reverse = Boolean(options.limit) } = options;

    let data: T[] | null = null;
    let queue: T[] = [];

    const renderTimer = new IdleTimer(() => {
      if (!data) throw new Error("should never happen: !data");
      if (queue.length) {
        if (options.reducer) {
          data = options.reducer(data, queue);
        } else {
          const lastData = data[data.length - 1];
          const firstQueue = queue[0];
          const seqKey =
            lastData &&
            firstQueue &&
            typeof lastData == "object" &&
            ["id", "timestamp"].find((key) => lastData[key] && firstQueue[key]);
          if (seqKey) {
            queue = queue.filter((x) => x[seqKey] > lastData[seqKey]);
          }
          data = slideWindow(data, queue, limit, limit ? limit * 1.2 : undefined);
          queue = [];
        }
      }
      setRenderData(data);
    });

    fetcher(url).then((history) => {
      data = history.map(transformHTTP) as T[];
      if (reverse) {
        data = data.reverse();
      }
      if (!renderTimer.running) renderTimer.schedule(200);
    });

    const handleWs = (msg: WsMsg) => {
      if (
        type === msg["event-type"] &&
        (!runId || msg.runid == runId) &&
        (!options.conditions?.series || options.conditions.series === msg.series) &&
        (!options.filterWS || options.filterWS(msg))
      ) {
        const transformed = transformWS(msg);
        queue.push(transformed);
        if (data && !renderTimer.running) renderTimer.schedule(200);
      }
    };

    const wsClient = getProject(projectId).wsClient;
    wsClient.wsListeners.add(handleWs);

    return () => {
      wsClient.wsListeners.delete(handleWs);
      renderTimer.cancel();
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [url]);

  // console.debug("useProjectData", options.type, renderData);
  return renderData;
}
