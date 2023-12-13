import { memo } from "react";
import { Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconInfoCircle } from "@douyinfe/semi-icons";
import { useProjectRunStatus } from "../../../hooks/useProject";
import Loading from "../../loading";
import { JsonViewThemed } from "./jsonView";

export const HyperParams = memo(({ projectId, runId, trigger = "click", position }: any) => {
  return (
    <Popover
      showArrow
      trigger={trigger}
      position={position}
      content={<HyperParamsContent projectId={projectId} runId={runId} />}
    >
      <IconInfoCircle />
    </Popover>
  );
});

const HyperParamsContent = memo(({ projectId, runId }: any) => {
  const runStatus = useProjectRunStatus(projectId, runId);
  const value = runStatus?.hyperparameters;
  return (
    <Space vertical>
      <Typography.Text type="primary">Hyperparameter</Typography.Text>
      {!runStatus ? (
        <Loading />
      ) : value == null ? (
        <Typography.Text type="tertiary">N/A</Typography.Text>
      ) : (
        <JsonViewThemed
          style={{ minWidth: 200, width: 400, maxHeight: "70vh", overflow: "auto" }}
          value={value}
          displayDataTypes={false}
        />
      )}
    </Space>
  );
});
