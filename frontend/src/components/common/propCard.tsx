import { Button, Card, Toast, Typography } from "@douyinfe/semi-ui";
import { IconCopy } from "@douyinfe/semi-icons";
import React, { memo } from "react";

export const PropCard = memo(({ propName, propValue }: { propName: string; propValue }) => {
  const { Text } = Typography;
  const content = Array.isArray(propValue) ? propValue.join(" ") : propValue;
  return (
    <Card
      shadows="hover"
      title={propName}
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
                Toast.info("Copied to clipboard");
              },
              () => {
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
