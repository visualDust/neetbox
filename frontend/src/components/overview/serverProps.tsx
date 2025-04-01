import { CardGroup } from "@douyinfe/semi-ui";
import React from "react";
import { useAPI } from "../../services/api";
import { PropCard } from "../common/propCard";

export function ServerPropsCard(): React.JSX.Element {
  const { data: serverIPs } = useAPI("/server/listips", { refreshInterval: 5000 });
  const hostname = serverIPs?.hostname;
  const ips = serverIPs?.ips || [];

  const { data: serverVersion } = useAPI("/server/version", { refreshInterval: 5000 });
  const version = serverVersion?.version;

  return (
    <div>
      <CardGroup spacing={10}>
        <PropCard propName="Hostname" propValue={hostname} />
        {ips.map((ip) => (
          <PropCard key={ip} propName="IP" propValue={ip} />
        ))}
        <PropCard propName="Server Version" propValue={version} />
      </CardGroup>
    </div>
  );
}
