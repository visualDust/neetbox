import { createContext, useContext, useEffect, useRef } from "react";
import { useAtom } from "jotai";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";
import { fetcher, useAPI } from "../services/api";
import { Condition, createCondition } from "../utils/condition";
import { ActionInfo, PlatformInfo, RunStatus } from "../services/types";
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
  const { data: series, mutate } = useAPI(`/project/${projectId}/series/${type}?runid=${runId}`);
  useProjectWebSocket(projectId, type, (msg) => {
    if (msg.series != null && series && !series.includes(msg.series) && msg.runid == runId) {
      mutate([...series, msg.series]);
    }
  });
  return series;
}

export function useProjectData<T = any>(options: {
  type: string;
  disable?: boolean;
  projectId: string;
  runId?: string;
  limit?: number;
  conditions?: Condition;
  filterWS?: (msg) => boolean;
  transformHTTP?: (data) => unknown;
  transformWS?: (msg) => unknown;
  onNewWSData?: (transformed) => void;
}) {
  const { type, projectId, runId, limit, transformWS = (x) => x, transformHTTP = (x) => x } = options;
  const wsReady = useProjectWebSocketReady(projectId);
  const url =
    options.disable || !wsReady
      ? null
      : `/project/${projectId}/${type}?${createCondition({
          runId,
          ...(!limit ? null : { limit, order: { id: "DESC" } }),
          ...options.conditions,
        })}`;
  const { data, mutate, isLoading } = useAPI(url, {
    fetcher: async (url) => {
      let result = (await fetcher(url)).map(transformHTTP);
      if (limit) {
        result = result.reverse();
      }
      return result;
    },
  });
  const flushQueue = () => {
    mutate(
      (arr) => {
        if (!arr) {
          console.warn("flushQueue called when the data is null/undefined");
          return arr;
        }
        let queue = refQueue.current.queue;
        if (!queue.length) {
          console.warn("flushQueue called when the queue is empty");
          return arr;
        }
        const lastData = arr[arr.length - 1];
        const firstQueue = queue[0];
        const seqKey =
          lastData && firstQueue && ["id", "timestamp"].find((key) => lastData[key] && firstQueue[key]);
        if (seqKey) {
          queue = queue.filter((x) => x[seqKey] > lastData[seqKey]);
        }
        return slideWindow(arr, queue, limit, limit ? limit * 1.2 : undefined);
      },
      {
        revalidate: false,
      },
    );
    refQueue.current.queue = [];
  };

  const refQueue = useRef<{ timer: IdleTimer; queue: T[] }>(null!);
  if (!refQueue.current) refQueue.current = { timer: new IdleTimer(flushQueue), queue: [] };

  useProjectWebSocket(projectId, type, (msg) => {
    if (options.disable) return;
    if (
      !runId ||
      (msg.runid == runId &&
        (!options.conditions?.series || options.conditions.series == msg.series) &&
        (!options.filterWS || options.filterWS(msg)))
    ) {
      const transformed = transformWS(msg);
      if (data && !isLoading && !refQueue.current.timer.running) {
        refQueue.current.timer.schedule(100);
      }
      refQueue.current.queue.push(transformed);
    }
  });

  useEffect(() => {
    if (data && !isLoading && refQueue.current.queue.length && !refQueue.current.timer) {
      flushQueue();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [data, isLoading]);

  useEffect(() => {
    refQueue.current.timer.cancel();
    refQueue.current.queue = [];
  }, [url]);

  // console.debug("useProjectData", options.type, data);
  return data as T[] | null;
}
