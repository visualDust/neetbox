import { useMemo } from "react";
import { ECharts } from "../../../echarts";
import { ProjectStatus } from "../../../../services/projects";

export const CPUGraph = ({
  hardwareData,
}: {
  hardwareData: Array<ProjectStatus["hardware"]>;
}) => {
  const cpus = hardwareData[0].value.cpus;
  const initialOption = () => {
    return {
      backgroundColor: 'transparent',
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      legend: {
        data: cpus.map((cpu) => `CPU${cpu.id}`),
      },
      xAxis: {
        type: "time",
      },
      yAxis: {
        type: "value",
        max: cpus.length * 100,
      },
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useMemo(() => {
    const latestTime = hardwareData[hardwareData.length - 1].timestamp;
    const newOption = {
      series: cpus.map((cpu) => ({
        name: `CPU${cpu.id}`,
        type: "line",
        stack: "cpu",
        areaStyle: {},
        symbol: null,
        data: hardwareData.map((x) => [
          x.timestamp * 1000,
          x.value.cpus[cpu.id].percent,
        ]),
      })),
      xAxis: {
        min: (latestTime - 60) * 1000,
        max: latestTime * 1000,
        data: new Array(10).fill(0).map((x, i) => i),
      },
    } as echarts.EChartsOption;
    return newOption;
  }, [hardwareData]);

  return (
    <ECharts
      initialOption={initialOption}
      updatingOption={updatingOption}
      style={{ height: "300px" }}
    />
  );
};
