import { useRef, useEffect, HTMLAttributes, useState } from "react";
import type * as echarts from "echarts";
import { useTheme } from "../hooks/useTheme";
import Loading from "./loading";

export interface EChartsProps {
  initialOption: () => echarts.EChartsOption;
  updatingOption: echarts.EChartsOption;
  style?: HTMLAttributes<HTMLElement>["style"];
}

export const ECharts = (props: EChartsProps) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef<echarts.ECharts>(null!);
  const [echartsModule, setEchartsModule] = useState<typeof echarts | null>(null);
  const { darkMode } = useTheme();

  useEffect(() => {
    import("echarts").then((mod) => setEchartsModule(mod));
  });

  useEffect(() => {
    if (echartsModule) {
      const chart = echartsModule.init(
        chartContainerRef.current,
        darkMode ? "dark" : null,
        // { renderer: "svg" },
      );

      chart.setOption(props.initialOption(), false, true);
      chart.setOption(props.updatingOption);
      chartRef.current = chart;

      let resizeTimer: number | null = null;
      const handleResize = () => {
        if (resizeTimer != null) clearTimeout(resizeTimer);
        resizeTimer = setTimeout(() => {
          chart?.resize();
        }, 20) as unknown as number;
      };
      const resizeObserver = new ResizeObserver(handleResize);
      resizeObserver.observe(chartContainerRef.current!);

      return () => {
        resizeObserver.disconnect();
        chart?.dispose();
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [echartsModule, darkMode]);

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.setOption(props.updatingOption);
    }
  }, [echartsModule, props.updatingOption]);

  return echartsModule ? (
    <div ref={chartContainerRef} style={props.style} />
  ) : (
    <Loading width={props.style?.width as string} height={props.style?.height as string} />
  );
};
