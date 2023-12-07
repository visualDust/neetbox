import { memo, useMemo } from "react";
import { Card, Space, Typography } from "@douyinfe/semi-ui";
import { useCurrentProject, useProjectWebSocket } from "../../../hooks/useProject";
import { ECharts } from "../../echarts";
import { useAPI } from "../../../services/api";
import { createCondition } from "../../../utils/condition";
import Loading from "../../loading";

export const Scatters = memo(() => {
  return (
    <Space style={{ marginBottom: "20px" }}>
      <AllScatterViewers />
    </Space>
  );
});

export const AllScatterViewers = memo(() => {
  const { projectId } = useCurrentProject();
  const { data: series, mutate } = useAPI(`/series/${projectId}/scatter`);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (msg.payload.series != null && !series.includes(msg.payload.series)) {
      mutate([...series, msg.payload.series]);
    }
  });
  return series?.map((s) => <ScatterViewer key={s} series={s} />) ?? <Loading />;
});

export const ScatterViewer = memo(({ series }: { series: string }) => {
  const { projectId, runId } = useCurrentProject();
  const { data, mutate } = useAPI(
    runId ? `/scatter/${projectId}/history?${createCondition({ series, runId })}` : null,
  );
  // const [data, setData] = useState<any[]>([]);
  useProjectWebSocket(projectId, "scatter", (msg) => {
    if (series == msg.payload.series && (!runId || runId == msg.runid)) {
      if (data) {
        mutate([...data, { metadata: msg.payload }], { revalidate: false });
      }
    }
  });

  const points = data?.map((x) => x.metadata) ?? [];

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
        min: "dataMin",
        // max: "dataMax",
      },
      yAxis: [
        {
          type: "value",
          // min: "dataMin",
          // max: "dataMax",
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const newOption = {
      series: [
        {
          name: series,
          type: "line",
          symbol: null,
          data: points?.map((x) => [x.x, x.y]),
        },
      ],
    } as echarts.EChartsOption;
    return newOption;
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [points]);

  return (
    <Card style={{ overflow: "visible" }}>
      <Space vertical>
        <Typography.Title heading={4}>scatter "{series}"</Typography.Title>
        {data ? (
          <ECharts
            initialOption={initialOption}
            updatingOption={updatingOption}
            style={{ height: "345px", width: "400px" }}
          />
        ) : (
          <Loading height="345px" width="400px" />
        )}
      </Space>
    </Card>
  );
});
