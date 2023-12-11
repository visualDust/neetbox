import { useCallback } from "react";
import { ECharts } from "../../../echarts";
import { RamInfo } from "../../../../services/types";
import { TimeDataMapper } from "../../../../utils/timeDataMapper";
import { getTimeAxisOptions } from "./utils";

export const RAMGraph = ({ data }: { data: TimeDataMapper<RamInfo> }) => {
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
          max: data.getValue(0).total,
        },
      ],
      series: [],
    } as echarts.EChartsOption;
  };

  const updatingOption = useCallback(() => {
    const newOption = {
      series: [
        {
          name: `RAM Used`,
          type: "line",
          areaStyle: {},
          symbol: null,
          data: data.map((timestamp, ram) => [new Date(timestamp), ram.used]),
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
