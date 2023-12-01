import { useMemo } from "react";
import { ECharts } from "../../../echarts";
import { ProjectStatus } from "../../../../services/types";
import { getTimeAxisOptions } from "./utils";

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
      title: {
        text: `GPU${gpuId}: ${gpus[gpuId].name}`,
        textStyle: {
          fontSize: 12,
        },
      },
      legend: {
        data: [`Load`, `Memory`],
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
            formatter: (x) => x.toFixed(1) + " GB",
          },
          max: gpus[gpuId].memoryTotal / 1024,
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const newOption = {
      series: [
        {
          name: `Load`,
          type: "line",
          areaStyle: null,
          symbol: null,
          data: hardwareData.map((x) => [new Date(x.timestamp), x.value.gpus[gpuId].load * 100]),
        },
        {
          name: `Memory`,
          type: "line",
          areaStyle: {},
          symbol: null,
          yAxisIndex: 1,
          data: hardwareData.map((x) => [new Date(x.timestamp), x.value.gpus[gpuId].memoryUsed / 1024]),
        },
      ],
      xAxis: getTimeAxisOptions(hardwareData),
    } as echarts.EChartsOption;
    return newOption;
  }, [gpuId, hardwareData]);

  return (
    <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
  );
};
