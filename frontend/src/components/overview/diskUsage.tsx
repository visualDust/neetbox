import { Card } from "@douyinfe/semi-ui";
import { ECharts } from "../common/echarts";
import Loading from "../common/loading";
import { useAPI } from "../../services/api";

interface DiskUsageData {
  total: number;
  used: number;
  neetbox: number;
  free: number;
}

export function DiskUsageChart({ data }: { data: DiskUsageData }) {
  const { used, neetbox, free } = data;
  const usedOther = used - neetbox;

  const seriesData = [
    { value: usedOther / 1e3, name: "Used (Other)" },
    { value: neetbox / 1e3, name: "Neetbox" },
    { value: free / 1e3, name: "Free" },
  ];

  const initialOption = (): echarts.EChartsOption => ({
    backgroundColor: "transparent",
    animation: true,
    tooltip: {
      trigger: "item",
      formatter: "{b}: {c} GB ({d}%)",
    },
    legend: {
      orient: "horizontal",
      left: "center",
      formatter: (name: string) => {
        const item = seriesData.find((d) => d.name === name);
        return item ? `${name}: ${item.value.toFixed(1)} GB` : name;
      },
    },
    series: [
      {
        type: "pie",
        radius: "60%",
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: "rgba(0, 0, 0, 0.5)",
          },
        },
        data: seriesData,
      },
    ],
  });

  const updatingOption = (): echarts.EChartsOption => ({
    series: [{ data: seriesData }],
  });

  return (
    <ECharts
      initialOption={initialOption}
      updatingOption={updatingOption}
      style={{ height: 400, width: "100%" }}
    />
  );
}

export function DiskUsageCard(): React.JSX.Element {
  const { data } = useAPI("/server/diskusage", { refreshInterval: 5000 });

  return (
    <Card
      shadows="hover"
      title="Disk Usage"
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
      style={{ width: "500px" }}
    >
      {data ? <DiskUsageChart data={data} /> : <Loading height="400px" width="100%" />}
    </Card>
  );
}
