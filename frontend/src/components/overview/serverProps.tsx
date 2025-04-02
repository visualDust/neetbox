import React from "react";
import { Descriptions, Card, Toast, Typography } from "@douyinfe/semi-ui";
import { IconCopy } from "@douyinfe/semi-icons";
import { useAPI } from "../../services/api";

export function ServerPropsCard(): React.JSX.Element {
  const { Text } = Typography;

  const { data: serverIPs } = useAPI("/server/listips", { refreshInterval: 5000 });
  const hostname = serverIPs?.hostname;
  const ips = serverIPs?.ips || [];

  const { data: serverVersion } = useAPI("/server/version", { refreshInterval: 5000 });
  const version = serverVersion?.version;

  const { data: configs } = useAPI("/server/configs", { refreshInterval: 5000 });

  const copyToClipboard = (value: string) => {
    navigator.clipboard
      .writeText(value)
      .then(() => {
        Toast.info("Copied to clipboard");
      })
      .catch(() => {
        Toast.error("Failed to copy");
      });
  };

  const mapValueToStyle = (value: any) => {
    if (typeof value === "boolean") {
      return <Text type={value ? "success" : "danger"}>{value ? "True" : "False"}</Text>;
    }
    return value;
  };

  const data = [
    { key: "Hostname", value: hostname },
    ...ips.map((ip) => ({
      key: "IP",
      value: (
        <div
          onClick={() => copyToClipboard(ip)}
          style={{ cursor: "pointer", display: "flex", alignItems: "center" }}
        >
          <Text>{ip}</Text>
        </div>
      ),
    })),
    { key: "Server Version", value: version },
    // configs
    ...Object.entries(configs || {}).map(([key, value]) => ({
      key: key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, " $1"),
      value: (
        <div
          onClick={() => copyToClipboard(String(value))}
          style={{ cursor: "pointer", display: "flex", alignItems: "center" }}
        >
          <Text>{mapValueToStyle(value)}</Text>
        </div>
      ),
    })),
  ];

  return (
    <Card
      shadows="hover"
      title="Server Properties"
      headerLine
      headerStyle={{ padding: "10px" }}
      bodyStyle={{
        padding: "10px",
        minHeight: "50px",
        display: "flex",
        flexDirection: "column",
        justifyContent: "center",
        textAlign: "center",
      }}
    >
      <Descriptions align="left" data={data} />
    </Card>
  );
}
