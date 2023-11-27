import React, { useEffect, useLayoutEffect, useRef, useState } from "react";
import { styled } from "styled-components";
import { LogData, useProjectLogs } from "../../../services/projects";
import "./logs.css";

interface Props {
  projectName: string;
}

function AutoScrolling({
  style,
  children,
}: React.PropsWithChildren<{ style: React.CSSProperties }>) {
  const containerRef = useRef<HTMLDivElement>(null!);
  const [following, setFollowing] = useState(true);
  const [renderingElement, setRenderingElement] = useState(children);
  useEffect(() => {
    const dom = containerRef.current;
    if (dom) {
      setFollowing(
        Math.abs(dom.scrollHeight - dom.clientHeight - dom.scrollTop) < 5
      );
    }
    setRenderingElement(children);
  }, [children]);
  useLayoutEffect(() => {
    const dom = containerRef.current;
    if (following) {
      dom.scroll({ top: dom.scrollHeight });
    }
  }, [renderingElement, following]);
  return (
    <div style={style} ref={containerRef}>
      {renderingElement}
    </div>
  );
}

export const Logs = React.memo(({ projectName }: Props) => {
  const logs = useProjectLogs(projectName);
  return (
    <AutoScrolling
      style={{ overflowY: "auto", height: "40vh" }}
      children={<LogItems logs={logs} />}
    />
  );
});

const LogItems = ({ logs }: { logs: LogData[] }) => {
  console.info("logitems render logs count", logs.length);
  return logs.map((x) => <LogItem key={x._id} data={x} />);
};

const LogItemContainer = styled.div`
  margin-bottom: 5px;
  font-family: "Courier New", Courier, monospace;
  font-size: 13px;

  .log-tag {
    display: inline-block;
    background-color: #ddd;
    padding: 0 3px;
    border-radius: 5px;
  }
  .log-prefix-info {
    background-color: #bbcffc;
  }
  .log-prefix-ok {
    background-color: #a2ffae;
  }
  .log-prefix-warning {
    background-color: #ede483;
  }
  .log-prefix-debug {
    background-color: #c483ed;
  }
  .log-prefix-error {
    background-color: #ffa2a2;
  }
`;

function getColorFromWhom(whom: string) {
  const hue =
    50 +
    ((whom
      .split("")
      .reduce((prev, char) => ((prev * 11) % 360) + char.charCodeAt(0), 0) *
      233) %
      200);
  return `hsl(${hue}, 70%, 80%)`;
}

const LogItem = React.memo(({ data }: { data: LogData }) => {
  let { prefix } = data;
  if (!prefix) prefix = "log";
  return (
    <LogItemContainer>
      <span className="log-tag log-datetime">{data.datetime}</span>{" "}
      <span className={`log-tag log-prefix log-prefix-${prefix}`}>
        {prefix}
      </span>{" "}
      <span
        className="log-tag log-whom"
        style={{ backgroundColor: getColorFromWhom(data.whom) }}
      >
        {data.whom}
      </span>{" "}
      {data.msg}
    </LogItemContainer>
  );
});
