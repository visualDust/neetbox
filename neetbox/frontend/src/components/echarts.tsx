import { useRef, useEffect, HTMLAttributes } from "react";
import * as echarts from "echarts";

export interface EChartsProps {
    initialOption: () => echarts.EChartsOption;
    updatingOption: echarts.EChartsOption;
    style?: HTMLAttributes<HTMLElement>['style'];
}

export const ECharts = (props: EChartsProps) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef<echarts.ECharts>(null!);

  useEffect(() => {
    const chart = echarts.init(chartContainerRef.current);

    chart.setOption(props.initialOption());
    chartRef.current = chart;

    return () => {
      chart.dispose();
    };
  }, []);

  useEffect(() => {
    chartRef.current.setOption(props.updatingOption);
  }, [props.updatingOption]);

  return <div ref={chartContainerRef} style={props.style} />;
};
