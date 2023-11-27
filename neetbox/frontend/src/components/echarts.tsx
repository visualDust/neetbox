import { useRef, useEffect, HTMLAttributes, useState } from "react";
import type * as echarts from "echarts";
import Loading from "./loading";

export interface EChartsProps {
  initialOption: () => echarts.EChartsOption;
  updatingOption: echarts.EChartsOption;
  style?: HTMLAttributes<HTMLElement>["style"];
}

export const ECharts = (props: EChartsProps) => {
  const chartContainerRef = useRef(null);
  const chartRef = useRef<echarts.ECharts>(null!);
  const [echartsModule, setEchartsModule] = useState<typeof echarts | null>(
    null,
  );

  useEffect(() => {
    import("echarts").then((mod) => setEchartsModule(mod));
  });

  useEffect(() => {
    if (echartsModule) {
      const chart = echartsModule.init(chartContainerRef.current);

      chart.setOption(props.initialOption());
      chartRef.current = chart;

      const handleResize = () => {
        chart?.resize();
      };
      window.addEventListener("resize", handleResize);

      return () => {
        window.removeEventListener("resize", handleResize);
        chart?.dispose();
      };
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [echartsModule]);

  useEffect(() => {
    if (chartRef.current) {
      chartRef.current.setOption(props.updatingOption);
    }
  }, [echartsModule, props.updatingOption]);

  return echartsModule ? (
    <div ref={chartContainerRef} style={props.style} />
  ) : (
    <Loading height={props.style?.height as string} />
  );
};
