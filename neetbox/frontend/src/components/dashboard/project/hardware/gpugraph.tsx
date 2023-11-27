import { useMemo } from "react";
import { ECharts } from "../../../echarts";
import { ProjectStatus } from "../../../../services/projects";

export const GPUGraph = ({
  hardwareData,
  gpuId,
}: {
  hardwareData: Array<ProjectStatus["hardware"]>;
  gpuId: number;
}) => {
  const gpus = hardwareData[0].value.gpus;
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
      legend: {
        data: [`GPU${gpuId} Load`, `GPU${gpuId} Memory`],
      },
      xAxis: {
        type: "time",
      },
      yAxis: [
        {
          type: "value",
          max: 100,
          axisLabel: {
            formatter: (x) => x + " %",
          },
        },
        {
          type: "value",
          position: "right",
          splitLine: null,
          axisLabel: {
            formatter: (x) => x + " MB",
          },
          max: gpus[gpuId].memoryTotal,
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const latestTime = hardwareData[hardwareData.length - 1].timestamp;
    const newOption = {
      series: [
        {
          name: `GPU${gpuId} Load`,
          type: "line",
          areaStyle: null,
          symbol: null,
          data: hardwareData.map((x) => [
            x.timestamp * 1000,
            x.value.gpus[gpuId].load * 100,
          ]),
        },
        {
          name: `GPU${gpuId} Memory`,
          type: "line",
          areaStyle: {},
          symbol: null,
          yAxisIndex: 1,
          data: hardwareData.map((x) => [
            x.timestamp * 1000,
            x.value.gpus[gpuId].memoryUsed,
          ]),
        },
      ],
      xAxis: {
        min: (latestTime - 60) * 1000,
        max: latestTime * 1000,
      },
    } as echarts.EChartsOption;
    return newOption;
  }, [hardwareData]);

  return (
    <ECharts
      initialOption={initialOption}
      updatingOption={updatingOption}
      style={{ height: "200px" }}
    />
  );
};
