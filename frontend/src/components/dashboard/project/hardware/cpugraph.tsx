import { useCallback } from "react";
import { ECharts } from "../../../echarts";
import { CpuInfo } from "../../../../services/types";
import { TimeDataMapper } from "../../../../utils/timeDataMapper";
import { getTimeAxisOptions } from "./utils";
import { GraphWrapper } from "./graphWrapper";

export const CPUGraph = ({ data }: { data: TimeDataMapper<CpuInfo[]> }) => {
  const cpus = data.getValue(0);
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
        left: 20,
        text: `CPU (${cpus.length} threads)`,
        textStyle: {
          fontSize: 12,
        },
      },
      // legend: {
      //   data: cpus.map((cpu) => `CPU${cpu.id}`),
      // },
      xAxis: {
        type: "time",
      },
      yAxis: {
        type: "value",
        max: cpus.length * 100,
        axisLabel: {
          formatter: (x) => x + " %",
        },
      },
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useCallback(() => {
    const newOption = {
      series: cpus.map((cpu) => ({
        name: `CPU${cpu.id}`,
        type: "line",
        stack: "cpu",
        areaStyle: {},
        symbol: null,
        data: data.map((timestamp, cpus) => [new Date(timestamp), cpus[cpu.id].percent]),
      })),
      xAxis: getTimeAxisOptions(data),
    } as echarts.EChartsOption;
    return newOption;
  }, [cpus, data]);

  return (
    <GraphWrapper title="CPU" lastValue={data.getValue(data.length - 1)}>
      <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
    </GraphWrapper>
  );
};
