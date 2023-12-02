import { useMemo } from "react";
import { ECharts } from "../../../echarts";
import { ProjectStatus } from "../../../../services/types";
import { getTimeAxisOptions } from "./utils";

export const CPUGraph = ({ hardwareData }: { hardwareData: Array<ProjectStatus["hardware"]> }) => {
  const cpus = hardwareData[0].value.cpus;
  console.info({ hardwareData });
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

  const updatingOption = useMemo(() => {
    const newOption = {
      series: cpus.map((cpu) => ({
        name: `CPU${cpu.id}`,
        type: "line",
        stack: "cpu",
        areaStyle: {},
        symbol: null,
        data: hardwareData.map((x) => [new Date(x.timestamp), x.value.cpus[cpu.id].percent]),
      })),
      xAxis: getTimeAxisOptions(hardwareData),
    } as echarts.EChartsOption;
    return newOption;
  }, [cpus, hardwareData]);

  return (
    <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
  );
};
