import { memo, useMemo } from "react";
import { Space, Select, Typography, Tag } from "@douyinfe/semi-ui";
import Loading from "../../loading";
import { useCurrentProject } from "../../../hooks/useProject";

export const RunSelect = memo(({ runIds, setRunId }: { runIds; setRunId }) => {
  const { runId, isOnlineRun } = useCurrentProject();
  const items = useMemo(
    () =>
      [...(runIds ?? [])]
        .reverse()
        .map((x) => ({ ...x, timestamp: x.timestamp.slice(0, 19).replace("T", " ") })),
    [runIds],
  );
  return (
    <Space style={{ width: "300px" }}>
      Run:
      {runIds ? (
        <Select
          value={runId}
          onChange={(x) => setRunId(x as string)}
          renderSelectedItem={(p) => (
            <>
              {isOnlineRun ? (
                <Tag color="green">Online</Tag>
              ) : runId != items[0].id ? (
                <Tag color="orange">History</Tag>
              ) : (
                <Tag color="red">Offline</Tag>
              )}
              {items.find((x) => x.id == p.value).timestamp}
            </>
          )}
        >
          {items.map((x) => (
            <Select.Option key={x.id} value={x.id}>
              {x.timestamp}{" "}
              <Typography.Text style={{ marginLeft: 5 }} type="tertiary">
                ({x.id})
              </Typography.Text>
            </Select.Option>
          ))}
        </Select>
      ) : (
        <Loading height="30px" />
      )}
    </Space>
  );
});
