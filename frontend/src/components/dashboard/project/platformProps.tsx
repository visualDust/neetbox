import React, { memo } from "react";
import { Toast, Button, Card, CardGroup, Typography } from "@douyinfe/semi-ui";
import { IconCopy } from "@douyinfe/semi-icons";
import { useMemoJSON } from "../../../hooks/useMemoJSON";
import { useCurrentProject, useProjectRunStatus } from "../../../hooks/useProject";
import { PlatformInfo } from "../../../services/types";
import { JsonPopover } from "./jsonView";

const PropCard = memo(({ propName, propValue }: { propName: string; propValue: PlatformInfo[string] }) => {
  const { Text } = Typography;
  const content = Array.isArray(propValue) ? propValue.join(" ") : propValue;
  const nameMapping = {
    username: "Launched by",
    machine: "Machine type",
    processor: "Processor name",
    os_name: "System/OS name",
    os_release: "Sys release ver",
    architecture: "Python arch.",
    python_build: "Python build",
    python_version: "Python version",
  };
  return (
    <Card
      shadows="hover"
      title={nameMapping[propName] ?? propName}
      headerLine={true}
      headerStyle={{ padding: "10px" }}
      bodyStyle={{
        padding: "10px",
        minHeight: "50px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        textAlign: "center",
      }}
      style={{ width: 260 }}
      headerExtraContent={
        <Button
          icon={<IconCopy />}
          style={{ marginRight: 10 }}
          size="small"
          onClick={() => {
            navigator.clipboard.writeText(content).then(
              () => {
                // copy success
                Toast.info("Copied to clipboard");
              },
              () => {
                // copy failed
                Toast.error("Failed to copy");
              },
            );
          }}
        ></Button>
      }
    >
      <Text>{content}</Text>
    </Card>
  );
});

export default function PlatformProps(): React.JSX.Element {
  const { projectId, runId } = useCurrentProject();
  const runStatus = useProjectRunStatus(projectId, runId);
  const memoData = useMemoJSON(runStatus?.platform);
  return (
    <div>
      <CardGroup spacing={10}>
        {(memoData &&
          Object.entries(memoData).map(([key, value]) => (
            <PropCard key={key} propName={key} propValue={value} />
          ))) || <Typography.Text>No Platform Info</Typography.Text>}
      </CardGroup>
    </div>
  );
}

export function PlatformTitleJson() {
  const { projectId, runId } = useCurrentProject();
  const runStatus = useProjectRunStatus(projectId, runId);
  return <JsonPopover value={runStatus?.platform} position="right" />;
}
