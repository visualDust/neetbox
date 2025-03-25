import { useEffect, useState } from "react";
import { getProject } from "../services/projects";
import { WsMsg } from "../services/projectWebsocket";
import { fetcher } from "../services/api";
import { Condition, createCondition } from "../utils/condition";
import { slideWindow } from "../utils/array";
import { IdleTimer } from "../utils/timer";
import { useProjectWebSocketReady } from "./useProject";

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
      : (customUrl ??
        `/project/${projectId}/${type}?${createCondition({
          runId,
          ...(!limit ? null : { limit, order: { id: "DESC" } }),
          ...options.conditions,
        })}`);

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
        type === msg.eventType &&
        (!runId || msg.runId == runId) &&
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
