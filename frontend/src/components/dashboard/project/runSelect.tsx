import { memo, startTransition, useEffect, useMemo } from "react";
import { Space, Select, Typography } from "@douyinfe/semi-ui";
import Loading from "../../loading";
import { useAPI } from "../../../services/api";
import { useCurrentProject } from "../../../hooks/useProject";

export const RunSelect = memo(() => {
  const { projectId, runId, setRunId } = useCurrentProject();
  const { data: runIds } = useAPI(`/runids/${projectId}`, { refreshInterval: 5000 });
  const sortedRunIds = useMemo(() => [...(runIds ?? [])].reverse(), [runIds]);
  useEffect(() => {
    if (runId === undefined && sortedRunIds.length) {
      setRunId(sortedRunIds[0]?.id);
    }
  }, [sortedRunIds, runId, setRunId]);
  return (
    <Space style={{ width: "240px" }}>
      Run:
      {runIds ? (
        <Select
          value={runId}
          onChange={(x) => setRunId(x as string)}
          renderSelectedItem={(p) =>
            p.value === undefined ? "All" : runIds.find((x) => x.id == p.value).timestamp
          }
        >
          {sortedRunIds.map((x) => (
            <Select.Option key={x.id} value={x.id}>
              {x.timestamp} <Typography.Text type="tertiary">({x.id})</Typography.Text>
            </Select.Option>
          ))}
        </Select>
      ) : (
        <Loading height="30px" />
      )}
    </Space>
  );
});
