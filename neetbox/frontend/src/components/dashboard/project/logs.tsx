import { useLayoutEffect, useRef } from "react";
import { styled } from "styled-components";
import { LogData, useProjectLogs } from "../../../services/projects";
import "./logs.css";

interface Props {
  projectName: string;
}

const LogsContainer = styled.div`
  height: 40vh;
  overflow-y: auto;
`;

export function Logs({ projectName }: Props) {
  const logs = useProjectLogs(projectName);
  const containerRef = useRef<HTMLDivElement>(null!);
  useLayoutEffect(() => {
    containerRef.current.scroll({ top: containerRef.current.scrollHeight });
  }, [logs]);
  return (
    <LogsContainer ref={containerRef}>
      {logs.map((x) => (
        <LogItem key={x._id} data={x} />
      ))}
    </LogsContainer>
  );
}

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
  .log-prefix-INFO {
    background-color: #bbcffc;
  }
  .log-prefix-OK {
    background-color: #a2ffae;
  }
  .log-prefix-WARNING {
    background-color: #ede483;
  }
  .log-prefix-ERROR {
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

function LogItem({ data }: { data: LogData }) {
  let { prefix } = data;
  if (!prefix) prefix = "LOG";
  return (
    <LogItemContainer>
      <span className="log-tag log-datetime">{data.datetime}</span>{" "}
      <span className={"log-tag log-prefix log-prefix-" + prefix}>
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
}
