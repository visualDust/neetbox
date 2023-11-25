import React from "react";
import { Toast, Button, Card, CardGroup, Typography } from "@douyinfe/semi-ui";
import { IconCopy } from "@douyinfe/semi-icons";

function PropCard({ propName, propValue }): React.JSX.Element {
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
            navigator.clipboard.writeText(propValue).then(
              () => {
                // copy success
                Toast.info("Copied to clipboard");
              },
              () => {
                // copy failed
                Toast.error("Failed to copy");
              }
            );
          }}
        ></Button>
      }
    >
      <Text>{content}</Text>
    </Card>
  );
}

export default function PlatformProps({ data }): React.JSX.Element {
  return (
    <div>
      <CardGroup spacing={10}>
        {Object.entries(data.value).map(([key, value]) => (
          <PropCard key={key} propName={key} propValue={value} />
        ))}
      </CardGroup>
    </div>
  );
}
