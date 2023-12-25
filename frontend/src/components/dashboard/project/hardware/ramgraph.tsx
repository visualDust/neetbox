import { useCallback } from "react";
import { ECharts } from "../../../echarts";
import { RamInfo } from "../../../../services/types";
import { TimeDataMapper } from "../../../../utils/timeDataMapper";
import { getTimeAxisOptions } from "./utils";
import { GraphWrapper } from "./graphWrapper";

export const RAMGraph = ({ data }: { data: TimeDataMapper<RamInfo> }) => {
  const initialOption = () => {
    return {
      backgroundColor: "transparent",
      animation: false,
      tooltip: {
        trigger: "axis",
      },
      title: {
        left: 20,
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
            formatter: (x) => (x / 1e3).toFixed(1) + " GB",
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
          name: `RAM Used(GB)`,
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
    <GraphWrapper title="Memory" lastValue={data.getValue(data.length - 1)}>
      <ECharts initialOption={initialOption} updatingOption={updatingOption} style={{ height: "200px" }} />
    </GraphWrapper>
  );
};
