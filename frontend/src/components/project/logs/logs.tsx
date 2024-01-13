import React, { memo, useEffect, useLayoutEffect, useRef, useState } from "react";
import { Button } from "@douyinfe/semi-ui";
import { IconAlignBottom } from "@douyinfe/semi-icons";
import { LogData } from "../../../services/types";
import "./logs.css";
import { useCurrentProject, useProjectData } from "../../../hooks/useProject";
import Loading from "../../common/loading";

function AutoScrolling({ style, children }: React.PropsWithChildren<{ style: React.CSSProperties }>) {
  const containerRef = useRef<HTMLDivElement>(null!);
  const scrollerRef = useRef<HTMLDivElement>(null!);
  const [following, setFollowing] = useState(true);
  const [renderingElement, setRenderingElement] = useState(children);
  const [height, setHeight] = useState(0);
  useLayoutEffect(() => {
    const observer = new ResizeObserver(() => {
      setHeight(containerRef.current!.clientHeight);
    });
    observer.observe(containerRef.current!, { box: "border-box" });
    return () => observer.disconnect();
  }, []);
  useEffect(() => {
    const dom = scrollerRef.current;
    if (dom) {
      setFollowing(Math.abs(dom.scrollHeight - dom.clientHeight - dom.scrollTop) < 10);
    }
    setRenderingElement(children);
  }, [children]);
  useLayoutEffect(() => {
    const dom = scrollerRef.current;
    if (following) {
      dom.scroll({ top: dom.scrollHeight });
    }
  }, [renderingElement, following, height]);
  return (
    <div style={{ position: "relative", ...style }} ref={containerRef}>
      <div style={{ overflowY: "auto", height: "100%", overflowAnchor: "none" }} ref={scrollerRef}>
        {renderingElement}
      </div>
      {!following && (
        <Button
          theme="solid"
          style={{ position: "absolute", bottom: "10px", left: "50%", transform: "translate(-50%, 0)" }}
          icon={<IconAlignBottom />}
          onClick={() => setFollowing(true)}
        >
          New Logs
        </Button>
      )}
    </div>
  );
}

export const Logs = React.memo(() => {
  const { projectId, runId } = useCurrentProject()!;
  const logs = useProjectData({
    projectId,
    type: "log",
    limit: 1000,
    runId,
    transformHTTP: (x) => ({
      id: x.id,
      timestamp: x.timestamp,
      series: x.series,
      ...x.metadata,
    }),
    transformWS: (x) => ({
      id: x.id,
      timestamp: x.timestamp,
      series: x.series,
      ...x.payload,
    }),
  });
  return logs ? (
    <AutoScrolling style={{ height: "40vh" }} children={<LogItems key={`LogItems-${runId}`} logs={logs} />} />
  ) : (
    <Loading size="large" height="40vh" />
  );
});

const LogItems = memo(({ logs }: { logs: LogData[] }) => {
  return logs.map((x) => <LogItem key={x.timestamp} data={x} />);
});

function getColorFromWhom(whom: string) {
  const hue =
    50 + ((whom.split("").reduce((prev, char) => ((prev * 11) % 360) + char.charCodeAt(0), 0) * 233) % 200);
  return `hsl(${hue}, 70%, var(--log-tag-bg-l))`;
}

const LogItem = React.memo(({ data }: { data: LogData }) => {
  let { series: prefix } = data;
  if (!prefix) prefix = "log";
  return (
    <div className="log-item">
      <span className="log-tag log-datetime">{data.timestamp}</span>{" "}
      <span className={`log-tag log-prefix log-prefix-${prefix}`}>{prefix}</span>{" "}
      <span className="log-tag log-whom" style={{ backgroundColor: getColorFromWhom(data.whom) }}>
        {data.whom}
      </span>{" "}
      {data.message}
    </div>
  );
});
