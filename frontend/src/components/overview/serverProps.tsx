import { CardGroup } from "@douyinfe/semi-ui";
import React from "react";
import { useAPI } from "../../services/api";
import { PropCard } from "../common/propCard";

export function ServerIpCard(): React.JSX.Element {
  const { data } = useAPI("/server/listips", { refreshInterval: 5000 });
  const hostname = data?.hostname;
  const ips = data?.ips || [];

  return (
    <div>
      <CardGroup spacing={10}>
        <PropCard propName="Hostname" propValue={hostname} />
        {ips.map((ip) => (
          <PropCard key={ip} propName="IP" propValue={ip} />
        ))}
      </CardGroup>
    </div>
  );
}
