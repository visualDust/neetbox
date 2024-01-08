import { useCallback } from "react";
import { ECharts } from "../../common/echarts";
import { GpuInfo } from "../../../services/types";
import { TimeDataMapper } from "../../../utils/timeDataMapper";
import { getTimeAxisOptions, percent2hue } from "./utils";
import { GraphWrapper } from "./graphWrapper";
import "./gpugraph.css";

export const GPUGraph = ({ data }: { data: TimeDataMapper<GpuInfo> }) => {
  const initialOption = () => {
    const gpu = data.getValue(0);
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
        left: 20,
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
  const lastValue = data.getValue(data.length - 1);
  return (
    <GraphWrapper title="GPU" lastValue={lastValue}>
      <div
        className="gpu-temperature"
        style={{
          backgroundColor:
            "hsl(" + percent2hue(lastValue.temperature) + ", 90%, var(--temperature-bg-brightness))",
        }}
      >
        {lastValue.temperature}℃
      </div>
      <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
    </GraphWrapper>
  );
};
