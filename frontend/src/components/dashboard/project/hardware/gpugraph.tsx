import { useCallback } from "react";
import { ECharts } from "../../../echarts";
import { GpuInfo } from "../../../../services/types";
import { TimeDataMapper } from "../../../../utils/timeDataMapper";
import { getTimeAxisOptions } from "./utils";

export const GPUGraph = ({ data }: { data: TimeDataMapper<GpuInfo> }) => {
  const initialOption = () => {
    const gpu = data.mapValue((x) => x)[0];
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
        text: `GPU${gpu.id}: ${gpu.name}`,
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
          max: gpu.memoryTotal / 1024,
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useCallback(() => {
    const newOption = {
      series: [
        {
          name: `Load`,
          type: "line",
          areaStyle: null,
          symbol: null,
          data: data.map((timestamp, gpu) => [new Date(timestamp), gpu.load * 100]),
        },
        {
          name: `Memory`,
          type: "line",
          areaStyle: {},
          symbol: null,
          yAxisIndex: 1,
          data: data.map((timestamp, gpu) => [new Date(timestamp), gpu.memoryUsed / 1024]),
        },
      ],
      xAxis: getTimeAxisOptions(data),
    } as echarts.EChartsOption;
    return newOption;
  }, [data]);

  return (
    <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
  );
};
