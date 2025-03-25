import { memo } from "react";
import { Button, Popover, Space, Typography } from "@douyinfe/semi-ui";
import { IconInfoCircle } from "@douyinfe/semi-icons";
import { useProjectRunStatus } from "../../hooks/useProject";
import Loading from "../common/loading";
import { JsonViewThemed } from "./jsonView";

export const HyperParams = memo(
  ({ projectId, runId, trigger = "click", position, children = <IconInfoCircle /> }: any) => {
    return (
      <Popover
        showArrow
        trigger={trigger}
        position={position}
        content={<HyperParamsContent projectId={projectId} runId={runId} />}
      >
        {children}
      </Popover>
    );
  },
);

const HyperParamsContent = memo(({ projectId, runId }: any) => {
  const [runStatus] = useProjectRunStatus(projectId, runId);
  const value = runStatus?.hyperparameters;
  return (
    <Space vertical>
      <Typography.Text type="primary">Hyperparameter</Typography.Text>
      {!runStatus ? (
        <Loading />
      ) : value == null ? (
        <Typography.Text type="tertiary">N/A</Typography.Text>
      ) : (
        <JsonViewThemed value={value} />
      )}
    </Space>
  );
});
