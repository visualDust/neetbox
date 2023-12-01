import React, { memo } from "react";
import { Toast, Button, Card, CardGroup, Typography } from "@douyinfe/semi-ui";
import { IconCopy } from "@douyinfe/semi-icons";
import { useMemoJSON } from "../../../hooks/useMemoJSON";
import { ProjectStatus } from "../../../services/types";

const PropCard = memo(
  ({ propName, propValue }: { propName: string; propValue: ProjectStatus["platform"]["value"][string] }) => {
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
  },
);

export default function PlatformProps({ data }: { data: ProjectStatus["platform"] }): React.JSX.Element {
  const memoData = useMemoJSON(data?.value);
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
