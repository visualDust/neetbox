import { useMemo } from "react";
import { ECharts } from "../../../echarts";
import { ProjectStatus } from "../../../../services/types";
import { getTimeAxisOptions } from "./utils";

export const RAMGraph = ({ hardwareData }: { hardwareData: Array<ProjectStatus["hardware"]> }) => {
  const initialOption = () => {
    return {
      backgroundColor: "transparent",
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      title: {
        text: `RAM`,
        textStyle: {
          fontSize: 12,
        },
      },
      grid: {
        top: 30,
        bottom: 30,
      },
      legend: {
        data: [`RAM Used`],
      },
      xAxis: {
        type: "time",
      },
      yAxis: [
        {
          type: "value",
          position: "right",
          axisLabel: {
            formatter: (x) => x.toFixed(1) + " GB",
          },
          max: hardwareData[0].value.ram.total,
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
          data: hardwareData.map((x) => [new Date(x.timestamp), x.value.ram.used]),
        },
      ],
      xAxis: getTimeAxisOptions(hardwareData),
    } as echarts.EChartsOption;
    return newOption;
  }, [hardwareData]);

  return (
    <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
  );
};
