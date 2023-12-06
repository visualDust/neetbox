import { memo, useMemo, useState } from "react";
import { Card, Space, Typography } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectWebSocket } from "../../../hooks/useProject";
import { ECharts } from "../../echarts";

export const Scatters = memo(() => {
  const { projectId } = useCurrentProject();
  const [series, setSeries] = useState<string[]>([]);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (msg.payload.series != null && !series.includes(msg.payload.series)) {
      setSeries([...series, msg.payload.series]);
    }
  });
  return (
    <Space style={{ marginBottom: "20px" }}>
      {series.map((s) => (
        <ScatterViewer key={s} series={s} />
      ))}
    </Space>
  );
});

export const ScatterViewer = memo(({ series }: { series: string }) => {
  const { projectId } = useCurrentProject();
  const [data, setData] = useState<any[]>([]);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (msg.payload.series != null && series == msg.payload.series) {
      setData([...data, msg.payload]);
    }
  });

  const initialOption = () => {
    return {
      backgroundColor: "transparent",
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      grid: {
        top: 30,
        bottom: 30,
      },
      xAxis: {
        type: "value",
      },
      yAxis: [
        {
          type: "value",
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const newOption = {
      series: [
        {
          name: `RAM Used`,
          type: "line",
          areaStyle: {},
          symbol: null,
          data: data.map((x) => [x.x, x.y]),
        },
      ],
    } as echarts.EChartsOption;
    return newOption;
  }, [data]);

  return (
    <Card>
      <Space vertical>
        <Typography.Title heading={4}>{series}</Typography.Title>
        <ECharts
          initialOption={initialOption}
          updatingOption={updatingOption}
          style={{ height: "300px", width: "400px" }}
        />
      </Space>
    </Card>
  );
});
